from functools import lru_cache
from pathlib import Path

import pandas as pd

from ..analysis.metrics import valid_frp
from ..response_cache import file_revision
from .archive import ARCHIVE_YEAR, archive_partitions, filter_dates, parquet_path, read_fire_columns


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


def observed_sources(year, partitions):
    return tuple((sensor, country, year, file_revision(parquet_path(sensor, country, year))) for sensor, country in partitions)


def map_file_sources(date_range, sensors, countries):
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


def longitude_spans(west, east):
    return [(west, 180), (-180, east)] if west > east else [(west, east)]


def observations_in_window(sources, bounds, date_range, clip=None, territory=None):
    west, south, east, north = bounds
    spans = longitude_spans(west, east)
    for boundary in (clip, territory.bounds if territory is not None else None):
        if boundary is None:
            continue
        clip_west, clip_south, clip_east, clip_north = boundary
        south, north = max(south, clip_south), min(north, clip_north)
        spans = [(max(left, a), min(right, b))
                 for left, right in spans for a, b in longitude_spans(clip_west, clip_east)]
        spans = [(left, right) for left, right in spans if left <= right]
        if south > north or not spans:
            return
    for kind, country, year, revision in sources:
        points = versioned_map_index(kind, revision)
        for left, right in spans:
            chunk = filter_dates(map_slice(points, left, south, right, north), *date_range)
            if territory is not None and not chunk.empty:
                chunk = chunk.loc[territory.covers(chunk["longitude"], chunk["latitude"])]
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
