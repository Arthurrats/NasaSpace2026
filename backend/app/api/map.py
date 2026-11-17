from functools import lru_cache, partial
from hashlib import sha256

import pandas as pd
from flask import Response, abort, jsonify, request

from ..analysis.activity import SOUTH_AMERICA
from ..analysis.metrics import period_windows
from ..data.archive import ARCHIVE_YEAR, COUNTRIES
from ..data.map_index import map_file_sources, observations_in_window
from ..maps.heat import heat_grid, heat_weight
from ..maps.markers import LEVEL_NAMES, MARKER_LIMIT, cluster_markers, sample_markers
from ..maps.territories import MAX_BODY, get_territory, register_territory
from ..maps.tiles import HEAT_PALETTES, HEAT_REFERENCE, PAD, TILE_SIZE, project_tile, render_heat_tile, render_tile, tile_edges
from ..response_cache import application_revision, cached_response
from . import api
from .filters import map_sources, requested_dates, requested_map_bbox


def requested_territory():
    return get_territory(request.args.get("territory"))


def map_revision():
    requested_territory()
    return map_file_sources(requested_dates(), *map_sources())


@lru_cache(maxsize=384)
def tile_groups(zoom, column, row, sources, date_range, clip, territory_key=None):
    bounds = tile_edges(zoom, column, row)
    records = observations_in_window(sources, bounds, date_range, clip, get_territory(territory_key))
    chunks = [chunk[["longitude", "latitude", "level"]] for _, _, _, chunk in records]
    if not chunks:
        return []
    frame = pd.concat(chunks, ignore_index=True)
    px, py = project_tile(frame["longitude"], frame["latitude"], zoom, column, row)
    frame = frame.loc[(px >= 0) & (px < TILE_SIZE) & (py >= 0) & (py < TILE_SIZE)].reset_index(drop=True)
    if len(frame) <= MARKER_LIMIT:
        return list(frame.itertuples(index=False, name=None))
    groups = cluster_markers(frame, frame["longitude"])
    return [(lng, lat, LEVEL_NAMES.index(level)) for _, lng, lat, level, _ in groups]


@api.post("/map/territories")
def map_territory():
    request.max_content_length = MAX_BODY
    return jsonify(id=register_territory(request.get_data(cache=False)))


@api.get("/map/tiles/<mode>/<int:zoom>/<int:column>/<int:row>.png")
@cached_response(map_revision, mimetype="image/png", max_age=30)
def map_tile(mode, zoom, column, row):
    if mode not in {"circle", "pixel", "cluster", "heat", "dots"} or zoom > 22 or column >= 2 ** zoom or row >= 2 ** zoom:
        abort(400, description="Bloco do mapa inválido.")
    date_range = requested_dates()
    sources = map_file_sources(date_range, *map_sources())
    clip = requested_map_bbox(None, allow_wrap=False, parameter="clip")
    territory = requested_territory()
    clip_pixels = partial(territory.clip_tile, zoom, column, row) if territory is not None else None
    if mode == "dots":
        clip = requested_map_bbox(SOUTH_AMERICA, allow_wrap=False)
    if mode == "cluster":
        size = 1 << zoom
        neighbors = sorted({(x % size, y) for x in range(column - 1, column + 2)
                            for y in range(max(0, row - 1), min(size, row + 2))})
        groups = [group for x, y in neighbors
                  for group in tile_groups(zoom, x, y, sources, date_range, clip, request.args.get("territory"))]
        lng, lat, level = zip(*groups) if groups else ([], [], [])
    else:
        west, south, east, north = tile_edges(zoom, column, row, PAD)
        west = west + 360 if west < -180 else west
        east = east - 360 if east > 180 else east
        if zoom == 0:
            west, east = -180, 180
        records = observations_in_window(sources, (west, south, east, north), date_range, clip, territory)
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
            image = render_heat_tile(zoom, column, row, frame["longitude"], frame["latitude"], frame["weight"], metric, palette, days, clip_pixels)
            return Response(image, mimetype="image/png")
        fields = [*coordinates, "level"]
        chunks = [chunk[fields] for _, _, _, chunk in records]
        frame = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=fields)
        lng, lat, level = frame["longitude"], frame["latitude"], frame["level"]
    return Response(render_tile(mode, zoom, column, row, lng, lat, level, clip_pixels), mimetype="image/png")


def requested_heat_metric():
    metric = request.args.get("metric", "detections")
    if metric not in HEAT_REFERENCE:
        abort(400, description="Métrica da camada de calor inválida.")
    return metric


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
    sources = map_file_sources(date_range, *map_sources())
    records = observations_in_window(sources, (west, south, east, north), date_range, clip, requested_territory())
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
