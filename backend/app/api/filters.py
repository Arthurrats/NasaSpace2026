import pandas as pd
from flask import abort, request

from ..data.archive import COLUMNS, COUNTRIES, FILE_PREFIX, filter_dates, load_file


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
