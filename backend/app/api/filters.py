import re

import pandas as pd
from flask import abort, request

from ..data.archive import COUNTRIES, FILE_PREFIX, filter_dates, load_file


def requested_dates() -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    dates = []
    for parameter in ("start_date", "end_date"):
        raw = request.args.get(parameter)
        try:
            if raw and not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", raw):
                raise ValueError
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
    sensors, countries = map_sources()
    dates = requested_dates()
    bbox = requested_map_bbox(None) if request.args.get("bbox") else None
    frames = [filter_dates(load_file(kind, name), *dates) for kind in sensors for name in countries]
    frame = pd.concat(frames, ignore_index=True)
    if bbox is not None:
        west, south, east, north = bbox
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
