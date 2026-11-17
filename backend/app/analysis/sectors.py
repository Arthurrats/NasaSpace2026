import pandas as pd


def sector_breaks(coordinates: pd.DataFrame) -> tuple:
    """Split the central coordinate range in thirds on each axis."""
    limits = coordinates[["longitude", "latitude"]].quantile([0.05, 0.95])
    lower, upper = limits.iloc[0], limits.iloc[1]
    third = (upper - lower) / 3
    return tuple(lower + third), tuple(upper - third)


def assign_sectors(frame: pd.DataFrame, breaks: tuple) -> pd.DataFrame:
    (west, south), (east, north) = breaks
    column = frame["longitude"].gt(west).astype(int) + frame["longitude"].gt(east).astype(int)
    row = frame["latitude"].lt(north).astype(int) + frame["latitude"].lt(south).astype(int)
    return frame.assign(sector=row * 3 + column)


def summarize_sectors(frame: pd.DataFrame) -> list[dict]:
    if frame.empty:
        return []
    daynight = frame["daynight"].astype("string").str.strip().str.upper()
    confidence = frame["confidence"].astype("string").str.strip().str.upper()
    is_modis = frame["sensor"].eq("MODIS")
    numeric = pd.to_numeric(confidence, errors="coerce")
    known = ((is_modis & numeric.between(0, 100)) | (~is_modis & confidence.isin(["L", "N", "H"]))).fillna(False)
    high = ((is_modis & numeric.between(80, 100)) | (~is_modis & confidence.eq("H"))).fillna(False)
    grouped = frame.assign(
        night=daynight.eq("N").fillna(False),
        classified_period=daynight.isin(["D", "N"]),
        high_confidence=high,
        classified_confidence=known,
    ).groupby("sector")
    stats = grouped.agg(
        detections=("latitude", "size"),
        active_days=("acq_date", "nunique"),
        frp_mw=("frp", "sum"),
        frp_samples=("frp", "count"),
        mean_frp_mw=("frp", "mean"),
        peak_frp_mw=("frp", "max"),
        night_count=("night", "sum"),
        period_count=("classified_period", "sum"),
        high_count=("high_confidence", "sum"),
        confidence_count=("classified_confidence", "sum"),
        sensors=("sensor", "nunique"),
        satellites=("satellite", "nunique"),
    )
    stats["p90_frp_mw"] = grouped["frp"].quantile(0.9)
    stats["frp_mw"] = stats["frp_mw"].where(stats["frp_samples"] > 0)
    stats["daily_average"] = stats["detections"] / stats["active_days"]
    stats["night_pct"] = stats["night_count"] * 100 / stats["period_count"].where(stats["period_count"] > 0)
    stats["high_pct"] = stats["high_count"] * 100 / stats["confidence_count"].where(stats["confidence_count"] > 0)
    stats = stats.drop(columns=["night_count", "period_count", "high_count", "confidence_count"]).reset_index()
    return stats.astype(object).where(stats.notna(), None).to_dict("records")


def rank_sectors(rows):
    if not rows:
        return {}
    return {
        metric: [row["sector"] for row in sorted((row for row in rows if row[metric] is not None),
                                                  key=lambda row: row[metric], reverse=True)]
        for metric in rows[0] if metric != "sector"
    }
