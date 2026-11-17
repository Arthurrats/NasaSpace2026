from functools import lru_cache

import pandas as pd
from flask import abort, request

from ..analysis.metrics import detection_series, geographic_grid, monthly_comparison, observation_metrics, rank_grid, valid_frp
from ..analysis.sectors import assign_sectors, rank_sectors, sector_breaks, summarize_sectors
from ..data.archive import ARCHIVE_YEAR, COUNTRIES, FILE_PREFIX, dataset_revision, load_versioned_file, parquet_path
from ..response_cache import cached_response, file_revision
from . import api
from .filters import query_frame, requested_dates


@api.get("/summary")
@cached_response(dataset_revision)
def summary() -> tuple[dict, int]:
    filters = {key: request.args[key] for key in ("sensor", "country", "start_date", "end_date", "bbox", "sector", "grid") if key in request.args}
    country = request.args.get("country", "all").strip().lower()
    name = next((name for name, slug in COUNTRIES.items() if country in (slug, name.lower())), None)
    sector = request.args.get("sector", "all")
    if sector != "all" and (name is None or sector not in {str(index) for index in range(9)}):
        abort(400, description="Selecione um setor entre 0 e 8 junto com um país.")
    frame = query_frame()
    frame = frame.assign(frp=valid_frp(frame["frp"]))
    by_sector = []
    if name and not frame.empty:
        frame = assign_sectors(frame, country_sector_breaks(name))
        by_sector = summarize_sectors(frame)
        if sector != "all":
            frame = frame.loc[frame["sector"] == int(sector)]
    if frame.empty:
        return {
            "filters": filters, "total_detections": 0, "total_frp_mw": 0,
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
        "filters": filters,
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
