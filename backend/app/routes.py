from __future__ import annotations

import os
from base64 import b64encode
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from struct import Struct

import pandas as pd
from flask import Blueprint, Response, abort, current_app, jsonify, request, session
from .analytics import detection_series, geographic_grid, monthly_comparison, observation_metrics, period_windows, rank_grid, valid_frp
from .fire_activity import ARCHIVE_YEAR, SOUTH_AMERICA, monthly_detections, summarize_activity
from .map_markers import LEVEL_NAMES, MARKER_LIMIT, cluster_markers, sample_markers
from .map_tiles import HEAT_PALETTES, HEAT_REFERENCE, PAD, TILE_SIZE, project_tile, render_heat_tile, render_tile, tile_edges
from .response_cache import application_revision, cached_response, file_revision
from .sectors import assign_sectors, rank_sectors, sector_breaks, summarize_sectors

api = Blueprint("api", __name__)
COUNTRIES = {
    "Argentina": "argentina", "Bolivia": "bolivia", "Brazil": "brasil",
    "Chile": "chile", "Colombia": "colombia", "Ecuador": "equador",
    "Guyana": "guiana", "Paraguay": "paraguai", "Peru": "peru",
    "Suriname": "suriname", "Uruguay": "uruguai", "Venezuela": "venezuela",
}
COLUMNS = [
    "latitude", "longitude", "acq_date", "acq_time", "satellite",
    "instrument", "confidence", "frp", "daynight", "type",
]
FILE_PREFIX = {"modis": "modis", "viirs": "viirs-jpss1"}
COUNTRY_ISO3 = {
    "Argentina": "ARG", "Bolivia": "BOL", "Brazil": "BRA", "Chile": "CHL",
    "Colombia": "COL", "Ecuador": "ECU", "Guyana": "GUY", "Paraguay": "PRY",
    "Peru": "PER", "Suriname": "SUR", "Uruguay": "URY", "Venezuela": "VEN",
}

def data_root() -> Path:
    configured = os.environ.get("PREVIA_DATA_DIR")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2] / "dados" / "parquet"


def parquet_path(sensor: str, country: str, year: int = ARCHIVE_YEAR) -> Path:
    return data_root() / sensor / f"{FILE_PREFIX[sensor]}_{year}_{country}.parquet"


def dataset_revision() -> tuple:
    return tuple(file_revision(parquet_path(sensor, country)) for sensor in FILE_PREFIX for country in COUNTRIES)


def archive_partitions() -> dict[int, set[tuple[str, str]]]:
    years = {}
    root = data_root()
    for sensor, prefix in FILE_PREFIX.items():
        for path in (root / sensor).glob(f"{prefix}_*.parquet"):
            year, _, country = path.stem.removeprefix(f"{prefix}_").partition("_")
            if len(year) == 4 and year[0] != "0" and year.isascii() and year.isdecimal() and country in COUNTRIES and path.is_file():
                years.setdefault(int(year), set()).add((sensor, country))
    return years


def archive_revision() -> tuple:
    paths = archive_partitions()
    return tuple(
        file_revision(parquet_path(sensor, country, year))
        for year, partitions in sorted(paths.items())
        for sensor, country in sorted(partitions)
    )


def read_fire_columns(path: Path, columns: list[str]) -> pd.DataFrame:
    if not path.is_file():
        abort(503, description="O arquivo de dados solicitado não está disponível.")
    try:
        return pd.read_parquet(path, columns=columns)
    except Exception:
        current_app.logger.exception("Could not read fire data file %s", path)
        abort(503, description="Não foi possível ler o conjunto de dados.")


def load_file(sensor: str, country: str) -> pd.DataFrame:
    return load_versioned_file(sensor, country, file_revision(parquet_path(sensor, country)))


@lru_cache(maxsize=24)
def load_versioned_file(sensor: str, country: str, revision: tuple) -> pd.DataFrame:
    frame = read_fire_columns(Path(revision[0]), COLUMNS)
    frame["sensor"] = sensor.upper()
    frame["country"] = country
    frame["acq_date"] = pd.to_datetime(frame["acq_date"], errors="coerce", utc=True).dt.normalize()
    return frame.dropna(subset=["latitude", "longitude", "acq_date"])


def requested_dates() -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    dates = []
    for parameter in ("start_date", "end_date"):
        raw = request.args.get(parameter)
        try:
            value = pd.to_datetime(raw, format="%Y-%m-%d", utc=True) if raw else None
        except (TypeError, ValueError):
            abort(400, description=f"{parameter} precisa estar no formato YYYY-MM-DD.")
        if value is not None and pd.isna(value):
            abort(400, description=f"{parameter} precisa estar no formato YYYY-MM-DD.")
        dates.append(value)
    start, end = dates
    if start is not None and end is not None and start > end:
        abort(400, description="start_date não pode ser posterior a end_date.")
    return start, end


def filter_dates(frame: pd.DataFrame, start: pd.Timestamp | None, end: pd.Timestamp | None) -> pd.DataFrame:
    if start is not None:
        frame = frame.loc[frame["acq_date"] >= start]
    if end is not None:
        frame = frame.loc[frame["acq_date"] <= end]
    return frame


def query_frame() -> pd.DataFrame:
    sensor = request.args.get("sensor", "all").strip().lower()
    if sensor not in {"all", "modis", "viirs"}:
        abort(400, description="sensor deve ser all, modis ou viirs.")

    requested_country = request.args.get("country", "all").strip().lower()
    country_names = list(COUNTRIES)
    if requested_country != "all":
        matched = [name for name in country_names if COUNTRIES[name] == requested_country or name.lower() == requested_country]
        if not matched:
            abort(400, description="country deve ser all ou o nome de um país sul-americano disponível.")
        country_names = matched

    frames = [load_file(kind, name) for kind in (["modis", "viirs"] if sensor == "all" else [sensor]) for name in country_names]
    frame = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=COLUMNS + ["sensor", "country"])

    frame = filter_dates(frame, *requested_dates())

    raw_bbox = request.args.get("bbox")
    if raw_bbox:
        try:
            west, south, east, north = (float(value) for value in raw_bbox.split(","))
        except (TypeError, ValueError):
            abort(400, description="bbox deve usar west,south,east,north em graus decimais.")
        if not (-180 <= west <= 180 and -180 <= east <= 180 and -90 <= south <= 90 and -90 <= north <= 90 and south < north):
            abort(400, description="bbox precisa conter coordenadas dentro dos limites geográficos.")
        longitude = frame["longitude"].between(west, east) if west <= east else (frame["longitude"] >= west) | (frame["longitude"] <= east)
        frame = frame.loc[longitude & frame["latitude"].between(south, north)]
    return frame


def pagination() -> tuple[int, int]:
    try:
        limit = int(request.args.get("limit", "1000"))
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        abort(400, description="limit e offset devem ser inteiros.")
    if not 1 <= limit <= 5000 or offset < 0:
        abort(400, description="limit deve estar entre 1 e 5000 e offset não pode ser negativo.")
    return limit, offset


def record(row: dict) -> dict:
    date = row["acq_date"]
    if pd.isna(date):
        date = None
    else:
        date = date.strftime("%Y-%m-%d")
    confidence = row["confidence"]
    if row["sensor"] == "VIIRS":
        intensity = {"H": "high", "N": "medium", "L": "low"}.get(str(confidence).upper(), "medium")
    else:
        confidence_value = pd.to_numeric(confidence, errors="coerce")
        intensity = "high" if pd.notna(confidence_value) and confidence_value >= 80 else "medium" if pd.notna(confidence_value) and confidence_value >= 50 else "low"
    return {
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "coordinates": [float(row["longitude"]), float(row["latitude"])],
        "date": date,
        "time": int(row["acq_time"]) if pd.notna(row["acq_time"]) else None,
        "country": row["country"],
        "sensor": row["sensor"],
        "satellite": str(row["satellite"]) if pd.notna(row["satellite"]) else None,
        "confidence": str(confidence) if pd.notna(confidence) else None,
        "frp_mw": float(row["frp"]) if pd.notna(row["frp"]) else None,
        "daynight": str(row["daynight"]) if pd.notna(row["daynight"]) else None,
        "type": int(row["type"]) if pd.notna(row["type"]) else None,
        "intensity": intensity,
    }


@api.get("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@api.route("/demo-session", methods=["GET", "POST", "DELETE"])
def demo_session():
    if request.method == "POST":
        if not request.is_json:
            abort(400, description="Envie a solicitação em JSON.")
        session["demo"] = True
    elif request.method == "DELETE":
        session.pop("demo", None)
    response = jsonify(active=session.get("demo", False))
    response.cache_control.no_store = True
    return response


@api.get("/countries")
def countries() -> tuple[dict, int]:
    return {"countries": [{"id": COUNTRIES[name], "name": name, "iso3": COUNTRY_ISO3[name]} for name in COUNTRIES]}, 200


@api.get("/activity")
@cached_response(archive_revision)
def fire_activity() -> tuple[dict, int]:
    sensors, countries = map_sources()
    west, south, east, north = requested_map_bbox(SOUTH_AMERICA, allow_wrap=False)
    scope_west, scope_south, scope_east, scope_north = SOUTH_AMERICA
    bounds = max(west, scope_west), max(south, scope_south), min(east, scope_east), min(north, scope_north)
    partitions = {(sensor, country) for sensor in sensors for country in countries}
    available_years = sorted(year for year, sources in archive_partitions().items() if partitions <= sources)
    if not available_years:
        abort(503, description="Não há um ano com arquivos para todos os sensores e países do recorte.")

    try:
        year = int(request.args.get("year", available_years[-1]))
    except ValueError:
        abort(400, description="year deve ser um ano inteiro.")
    if year not in available_years:
        abort(400, description="O ano não está disponível para todos os sensores e países do recorte.")

    past = [previous for previous in available_years if previous < year]
    history = {previous: monthly_detections(activity_frame(previous, partitions, bounds)) for previous in past} if len(past) >= 2 else {}
    return summarize_activity(activity_frame(year, partitions, bounds), year, available_years, history), 200


@api.get("/fires")
@cached_response(dataset_revision)
def fires() -> tuple[dict, int]:
    limit, offset = pagination()
    frame = query_frame().sort_values(["acq_date", "acq_time"], ascending=False)
    total = len(frame)
    selected = frame.iloc[offset:offset + limit]
    return {
        "data": [record(row) for row in selected.to_dict(orient="records")],
        "pagination": {"limit": limit, "offset": offset, "total": total, "has_more": offset + len(selected) < total},
        "meta": {"synthetic": False, "sensors": sorted(frame["sensor"].unique().tolist()), "unit": "satellite detections"},
    }, 200


HEAT_GRID_WIDTH = 512
HEAT_GRID_HEIGHT = 384
HEAT_BIN = Struct("<If")


def heat_grid(longitude: pd.Series, latitude: pd.Series, weight: pd.Series) -> dict:
    west, south = float(longitude.min()), float(latitude.min())
    lng_span = max(float(longitude.max()) - west, 1e-9)
    lat_span = max(float(latitude.max()) - south, 1e-9)
    x = ((longitude - west) / lng_span * HEAT_GRID_WIDTH).clip(0, HEAT_GRID_WIDTH - 1).astype(int)
    y = ((latitude - south) / lat_span * HEAT_GRID_HEIGHT).clip(0, HEAT_GRID_HEIGHT - 1).astype(int)
    sums = weight.groupby(y * HEAT_GRID_WIDTH + x).sum()
    occupied = sums[sums.gt(0)]
    data = bytearray(len(occupied) * HEAT_BIN.size)
    for index, (cell, value) in enumerate(occupied.items()):
        HEAT_BIN.pack_into(data, index * HEAT_BIN.size, int(cell), float(value))
    return {
        "columns": HEAT_GRID_WIDTH,
        "rows": HEAT_GRID_HEIGHT,
        "west": west,
        "south": south,
        "lng_step": lng_span / HEAT_GRID_WIDTH,
        "lat_step": lat_span / HEAT_GRID_HEIGHT,
        "bins": b64encode(data).decode("ascii"),
    }


@lru_cache(maxsize=24)
def versioned_map_index(sensor: str, revision: tuple) -> pd.DataFrame:
    frame = read_fire_columns(Path(revision[0]), ["longitude", "latitude", "confidence", "acq_date", "frp", "daynight"])
    valid = frame["longitude"].between(-180, 180) & frame["latitude"].between(-90, 90)
    frame["acq_date"] = pd.to_datetime(frame["acq_date"], errors="coerce", utc=True).dt.normalize()
    valid &= frame["acq_date"].notna()
    points = frame.loc[valid].copy()
    points["frp"] = valid_frp(points["frp"]).fillna(0)
    points["night"] = points.pop("daynight").astype("string").str.strip().str.upper().eq("N").fillna(False)
    if sensor == "viirs":
        confidence = points["confidence"].astype(str).str.upper()
        points["level"] = confidence.map({"L": 0, "N": 1, "H": 2}).fillna(1).astype("int8")
    else:
        confidence = pd.to_numeric(points["confidence"], errors="coerce").fillna(0)
        points["level"] = (confidence.ge(50).astype("int8") + confidence.ge(80).astype("int8"))
    return points.drop(columns="confidence").sort_values("longitude", kind="stable")


def map_slice(points: pd.DataFrame, west: float, south: float, east: float, north: float) -> pd.DataFrame:
    longitude = points["longitude"]
    start = longitude.searchsorted(west, side="left")
    end = longitude.searchsorted(east, side="right")
    candidates = points.iloc[start:end]
    return candidates.loc[candidates["latitude"].between(south, north)]


def map_sources() -> tuple:
    sensor = request.args.get("sensor", "all").strip().lower()
    if sensor not in {"all", *FILE_PREFIX}:
        abort(400, description="sensor deve ser all, modis ou viirs.")
    country = request.args.get("country", "all").strip().lower()
    countries = tuple(name for name, slug in COUNTRIES.items() if country in {"all", slug, name.lower()})
    if not countries:
        abort(400, description="País indisponível.")
    return tuple(FILE_PREFIX) if sensor == "all" else (sensor,), countries


def requested_map_bbox(default=(-180, -90, 180, 90), *, allow_wrap=True, parameter="bbox"):
    raw = request.args.get(parameter)
    if raw is None:
        return default
    try:
        west, south, east, north = map(float, raw.split(","))
    except ValueError:
        abort(400, description="bbox deve usar oeste,sul,leste,norte.")
    if not (-180 <= west <= 180 and -180 <= east <= 180 and -90 <= south < north <= 90):
        abort(400, description="bbox contém coordenadas inválidas.")
    east_unwrapped = east + 360 if allow_wrap and west > east else east
    if east_unwrapped <= west:
        abort(400, description="bbox precisa ter largura positiva.")
    return west, south, east, north


def observed_sources(year, partitions):
    return tuple((sensor, country, year, file_revision(parquet_path(sensor, country, year))) for sensor, country in partitions)


def map_file_sources(date_range):
    sensors, countries = map_sources()
    selected = [(sensor, country) for sensor in sensors for country in countries]
    start, end = date_range
    if (start is None and end is None) or (start is not None and end is not None and start.year == end.year == ARCHIVE_YEAR):
        return observed_sources(ARCHIVE_YEAR, selected)

    inventory = archive_partitions()
    # Keep the original archive's missing-file behavior for existing map callers.
    inventory[ARCHIVE_YEAR] = set(selected)
    return tuple(
        source for year, partitions in sorted(inventory.items())
        if (start is None or year >= start.year) and (end is None or year <= end.year)
        for source in observed_sources(year, [pair for pair in selected if pair in partitions])
    )


def map_revision():
    return map_file_sources(requested_dates())


def observations_in_window(sources, bounds, date_range, clip=None):
    west, south, east, north = bounds
    spans = [(west, 180), (-180, east)] if west > east else [(west, east)]
    if clip:
        clip_west, clip_south, clip_east, clip_north = clip
        south, north = max(south, clip_south), min(north, clip_north)
        spans = [(max(left, clip_west), min(right, clip_east)) for left, right in spans]
        spans = [(left, right) for left, right in spans if left <= right]
        if south > north or not spans:
            return
    for kind, country, year, revision in sources:
        points = versioned_map_index(kind, revision)
        for left, right in spans:
            chunk = filter_dates(map_slice(points, left, south, right, north), *date_range)
            if not chunk.empty:
                yield kind, country, year, chunk


def activity_frame(year, partitions, bounds):
    west, south, east, north = bounds
    fields = ["acq_date", "longitude", "latitude", "frp"]
    if west <= east and south <= north:
        dates = pd.Timestamp(f"{year}-01-01", tz="UTC"), pd.Timestamp(f"{year}-12-31", tz="UTC")
        sources = observed_sources(year, sorted(partitions))
        chunks = [chunk[fields] for _, _, _, chunk in observations_in_window(sources, bounds, dates)]
        if chunks:
            return pd.concat(chunks, ignore_index=True)
    return pd.DataFrame({"acq_date": pd.DatetimeIndex([], tz="UTC"), "longitude": [], "latitude": [], "frp": []})


@lru_cache(maxsize=384)
def tile_groups(zoom, column, row, sources, date_range, clip):
    bounds = tile_edges(zoom, column, row)
    chunks = [chunk[["longitude", "latitude", "level"]] for _, _, _, chunk in observations_in_window(sources, bounds, date_range, clip)]
    if not chunks:
        return []
    frame = pd.concat(chunks, ignore_index=True)
    px, py = project_tile(frame["longitude"], frame["latitude"], zoom, column, row)
    frame = frame.loc[(px >= 0) & (px < TILE_SIZE) & (py >= 0) & (py < TILE_SIZE)].reset_index(drop=True)
    if len(frame) <= MARKER_LIMIT:
        return list(frame.itertuples(index=False, name=None))
    groups = cluster_markers(frame, frame["longitude"])
    return [(lng, lat, LEVEL_NAMES.index(level)) for _, lng, lat, level, _ in groups]


@api.get("/map/tiles/<mode>/<int:zoom>/<int:column>/<int:row>.png")
@cached_response(map_revision, mimetype="image/png", max_age=30)
def map_tile(mode, zoom, column, row):
    if mode not in {"circle", "pixel", "cluster", "heat", "dots"} or zoom > 22 or column >= 2 ** zoom or row >= 2 ** zoom:
        abort(400, description="Bloco do mapa inválido.")
    date_range = requested_dates()
    sources = map_file_sources(date_range)
    clip = requested_map_bbox(None, allow_wrap=False, parameter="clip")
    if mode == "dots":
        clip = requested_map_bbox(SOUTH_AMERICA, allow_wrap=False)
    if mode == "cluster":
        size = 1 << zoom
        neighbors = sorted({(x % size, y) for x in range(column - 1, column + 2)
                            for y in range(max(0, row - 1), min(size, row + 2))})
        groups = [group for x, y in neighbors for group in tile_groups(zoom, x, y, sources, date_range, clip)]
        lng, lat, level = zip(*groups) if groups else ([], [], [])
    else:
        west, south, east, north = tile_edges(zoom, column, row, PAD)
        west = west + 360 if west < -180 else west
        east = east - 360 if east > 180 else east
        if zoom == 0:
            west, east = -180, 180
        records = observations_in_window(sources, (west, south, east, north), date_range, clip)
        coordinates = ["longitude", "latitude"]
        if mode == "heat":
            metric = requested_heat_metric()
            palette = request.args.get("palette", "default")
            if palette not in HEAT_PALETTES:
                abort(400, description="palette deve ser default ou accessible.")
            start, end = date_range
            days = (end - start).days + 1 if start is not None and end is not None else 365
            chunks = [chunk[coordinates].assign(weight=heat_weight(chunk, metric)) for _, _, _, chunk in records]
            frame = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=[*coordinates, "weight"])
            image = render_heat_tile(zoom, column, row, frame["longitude"], frame["latitude"], frame["weight"], metric, palette, days)
            return Response(image, mimetype="image/png")
        fields = [*coordinates, "level"]
        chunks = [chunk[fields] for _, _, _, chunk in records]
        frame = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=fields)
        lng, lat, level = frame["longitude"], frame["latitude"], frame["level"]
    return Response(render_tile(mode, zoom, column, row, lng, lat, level), mimetype="image/png")


def requested_heat_metric():
    metric = request.args.get("metric", "detections")
    if metric not in HEAT_REFERENCE:
        abort(400, description="Métrica da camada de calor inválida.")
    return metric


def heat_weight(chunk, metric):
    if metric == "frp":
        return chunk["frp"]
    if metric == "night":
        return chunk["night"]
    if metric == "high":
        return chunk["level"].eq(2)
    return 1


@api.get("/map/foci")
@cached_response(map_revision)
def map_foci():
    date_range = requested_dates()
    density = request.args.get("layer") == "heat"
    show_samples = request.args.get("markers") == "points"
    metric = requested_heat_metric() if density else "detections"
    west, south, east, north = requested_map_bbox()
    clip = requested_map_bbox(None, allow_wrap=False, parameter="clip")
    wraps = west > east
    sources = map_file_sources(date_range)
    records = observations_in_window(sources, (west, south, east, north), date_range, clip)
    if request.args.get("format") == "count":
        total = sum(len(chunk) for _, _, _, chunk in records)
        revision = sha256(repr((application_revision(), sources)).encode()).hexdigest()[:16]
        return jsonify(total=total, revision=revision)
    chunks = []
    fields = ["longitude", "latitude", "level"]
    if density:
        fields.append("weight")
    for kind, name, year, chunk in records:
        if density:
            chunk = chunk.assign(weight=heat_weight(chunk, metric))
        source = f"{kind}:{COUNTRIES[name]}"
        if year != ARCHIVE_YEAR:
            source += f":{year}"
        chunks.append((source, chunk[fields]))

    total = sum(len(chunk) for _, chunk in chunks)
    if total <= MARKER_LIMIT:
        data = [
            [f"{source}:{index}", round(lng, 6), round(lat, 6), LEVEL_NAMES[level], 1, *map(float, weights)]
            for source, chunk in chunks
            for index, lng, lat, level, *weights in chunk.itertuples(name=None)
        ]
    else:
        visible = pd.concat([chunk for _, chunk in chunks], ignore_index=True)
        longitude = visible["longitude"]
        if wraps:
            longitude = longitude.where(longitude >= west, longitude + 360)
        if not density:
            data = sample_markers(visible) if show_samples else cluster_markers(visible, longitude)
            return jsonify(data=data, total=total)
        latitude = visible["latitude"]
        if request.args.get("format") == "grid":
            return jsonify(grid=heat_grid(longitude, latitude, visible["weight"]), total=total)
        # Keep the older JSON heat format available to other callers.
        width, height = 192, 144
        lng_min, lat_min = longitude.min(), latitude.min()
        lng_span = max(longitude.max() - lng_min, 1e-9)
        lat_span = max(latitude.max() - lat_min, 1e-9)
        columns = ((longitude - lng_min) / lng_span * width).clip(0, width - 1).astype(int)
        rows = ((latitude - lat_min) / lat_span * height).clip(0, height - 1).astype(int)
        cells = visible.assign(longitude=longitude, cell=rows * width + columns).groupby("cell").agg(
            longitude=("longitude", "mean"), latitude=("latitude", "mean"),
            level=("level", "max"), count=("level", "size"), weight=("weight", "sum"),
        )
        data = [
            [f"cell:{cell}", round((lng + 180) % 360 - 180, 6), round(lat, 6), LEVEL_NAMES[level], count, float(weight)]
            for cell, lng, lat, level, count, weight in cells.itertuples(name=None)
        ]
    return jsonify(data=data, total=total)


@api.get("/map/timeline")
def map_timeline():
    start, end = requested_dates()
    step = request.args.get("step", "month")
    if step not in {"day", "week", "month"}:
        abort(400, description="step deve ser day, week ou month.")
    if start is None or end is None or (end - start).days > 366:
        abort(400, description="Informe início e fim para um intervalo de até 367 dias.")
    return {"frames": period_windows(start, end, step)}, 200


@api.get("/summary")
@cached_response(dataset_revision)
def summary() -> tuple[dict, int]:
    frame = query_frame()
    frame = frame.assign(frp=valid_frp(frame["frp"]))
    by_sector = []
    country = request.args.get("country", "all").strip().lower()
    name = next((name for name, slug in COUNTRIES.items() if country in (slug, name.lower())), None)
    sector = request.args.get("sector", "all")
    if sector != "all" and (name is None or sector not in {str(index) for index in range(9)}):
        abort(400, description="Selecione um setor entre 0 e 8 junto com um país.")
    if name and not frame.empty:
        frame = assign_sectors(frame, country_sector_breaks(name))
        by_sector = summarize_sectors(frame)
        if sector != "all":
            frame = frame.loc[frame["sector"] == int(sector)]
    if frame.empty:
        return {
            "filters": dict(request.args), "total_detections": 0, "total_frp_mw": 0,
            "average_daily_detections": 0, "peak_day": None, "by_country": [],
            "by_day": [], "by_month": [], "by_sensor": [], "by_intensity": [],
            "by_country_month": [], "by_sensor_month": [], "by_daynight": [],
            "by_satellite": [], "by_sector": by_sector,
            "series": {"day": [], "week": [], "month": []},
            "monthly_comparison": {"country": [], "sensor": []},
            "grid": [], "grid_rankings": rank_grid([]), "sector_rankings": rank_sectors(by_sector), **observation_metrics(frame),
            "meta": {"synthetic": False, "unit": "satellite detections"},
        }, 200

    country_counts = frame.groupby("country", observed=True).agg(detections=("latitude", "size"), frp_mw=("frp", "sum")).reset_index()
    country_counts = country_counts.sort_values("detections", ascending=False)
    daily = frame.groupby("acq_date", observed=True).agg(detections=("latitude", "size"), frp_mw=("frp", "sum")).reset_index()
    daily["date"] = daily.pop("acq_date").dt.strftime("%Y-%m-%d")
    monthly = frame.assign(month=frame["acq_date"].dt.strftime("%Y-%m"))
    metrics = {"detections": ("latitude", "size"), "frp_mw": ("frp", "sum")}
    monthly_counts = monthly.groupby("month", observed=True).agg(**metrics).reset_index()
    country_month_counts = monthly.groupby(["country", "month"], observed=True).agg(**metrics).reset_index()
    sensor_month_counts = monthly.groupby(["sensor", "month"], observed=True).agg(**metrics).reset_index()
    start, end = requested_dates()
    archive_start = pd.Timestamp(f"{ARCHIVE_YEAR}-01-01", tz="UTC")
    archive_end = pd.Timestamp(f"{ARCHIVE_YEAR}-12-31", tz="UTC")
    series = detection_series(daily, max(start or archive_start, archive_start), min(end or archive_end, archive_end))
    months = [row["start_date"][:7] for row in series["month"]]
    sensor_counts = frame.groupby("sensor", observed=True).agg(detections=("latitude", "size"), frp_mw=("frp", "sum")).reset_index()
    daynight = frame["daynight"].astype("string").str.strip().str.upper().map({"D": "day", "N": "night"}).fillna("unknown")
    satellites = frame["satellite"].astype("string").str.strip().replace("", pd.NA).fillna("unknown")

    numeric_confidence = pd.to_numeric(frame["confidence"], errors="coerce")
    intensity = pd.Series("low", index=frame.index)
    intensity = intensity.mask(numeric_confidence >= 50, "medium")
    intensity = intensity.mask(numeric_confidence >= 80, "high")
    viirs_confidence = frame["confidence"].fillna("").astype(str).str.upper()
    intensity = intensity.mask((frame["sensor"] == "VIIRS") & viirs_confidence.eq("N"), "medium")
    intensity = intensity.mask((frame["sensor"] == "VIIRS") & viirs_confidence.eq("H"), "high")
    intensity_counts = intensity.value_counts().reindex(["high", "medium", "low"], fill_value=0)
    peak = daily.loc[daily["detections"].idxmax()]
    grid = geographic_grid(frame) if request.args.get("grid") == "1" else []
    return {
        "filters": dict(request.args),
        "total_detections": int(len(frame)),
        "total_frp_mw": float(frame["frp"].sum()),
        "average_daily_detections": round(len(frame) / len(daily), 1),
        "peak_day": {"date": peak["date"], "detections": int(peak["detections"])},
        "by_country": [{"country": row.country, "detections": int(row.detections), "frp_mw": float(row.frp_mw)} for row in country_counts.itertuples()],
        "by_day": daily.to_dict("records"),
        "by_month": monthly_counts.to_dict("records"),
        "by_country_month": country_month_counts.to_dict("records"),
        "by_sensor_month": sensor_month_counts.to_dict("records"),
        "series": series,
        "monthly_comparison": {
            "country": monthly_comparison(country_month_counts, "country", months),
            "sensor": monthly_comparison(sensor_month_counts, "sensor", months),
        },
        "by_daynight": [{"period": period, "detections": int(count)} for period, count in daynight.value_counts().items()],
        "by_satellite": [{"satellite": satellite, "detections": int(count)} for satellite, count in satellites.value_counts().items()],
        "by_sensor": [{"sensor": row.sensor, "detections": int(row.detections), "frp_mw": float(row.frp_mw)} for row in sensor_counts.itertuples()],
        "by_intensity": [{"intensity": level, "detections": int(count)} for level, count in intensity_counts.items()],
        "by_sector": by_sector,
        "sector_rankings": rank_sectors(by_sector),
        "grid": grid,
        "grid_rankings": rank_grid(grid),
        **observation_metrics(frame),
        "meta": {"synthetic": False, "sensors": sorted(frame["sensor"].unique().tolist()), "unit": "satellite detections"},
    }, 200


def country_sector_breaks(country: str) -> tuple:
    revisions = tuple((sensor, file_revision(parquet_path(sensor, country))) for sensor in FILE_PREFIX)
    return versioned_sector_breaks(country, revisions)


@lru_cache(maxsize=12)
def versioned_sector_breaks(country: str, revisions: tuple) -> tuple:
    reference = pd.concat([load_versioned_file(sensor, country, revision)[["latitude", "longitude"]] for sensor, revision in revisions])
    valid = reference["longitude"].between(-180, 180) & reference["latitude"].between(-90, 90)
    return sector_breaks(reference.loc[valid])
