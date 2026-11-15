from heapq import nlargest
from operator import itemgetter

import pandas as pd


def period_windows(start, end, step):
    windows = []
    while start <= end:
        following = start + (pd.offsets.MonthBegin() if step == "month" else pd.Timedelta(days=1 if step == "day" else 7))
        last = min(following - pd.Timedelta(days=1), end)
        windows.append({"start_date": start.date().isoformat(), "end_date": last.date().isoformat()})
        start = following
    return windows


def detection_series(daily, start, end):
    by_date = daily.set_index("date")
    series = {}
    for step in ("day", "week", "month"):
        rows = []
        for window in period_windows(start, end, step):
            subset = by_date.loc[window["start_date"]:window["end_date"]]
            rows.append({**window, "detections": int(subset["detections"].sum()), "frp_mw": float(subset["frp_mw"].sum())})
        series[step] = rows
    return series


def monthly_comparison(rows, dimension, months):
    index = pd.MultiIndex.from_product((rows[dimension].unique(), months), names=[dimension, "month"])
    return rows.set_index([dimension, "month"]).reindex(index, fill_value=0).reset_index().to_dict("records")


def valid_frp(values: pd.Series) -> pd.Series:
    power = pd.to_numeric(values, errors="coerce").astype("float64")
    return power.where(power.ge(0) & power.lt(float("inf")))


def observation_metrics(frame: pd.DataFrame) -> dict:
    time = pd.to_numeric(frame["acq_time"], errors="coerce")
    valid_time = time.between(0, 2359) & time.mod(100).lt(60) & time.mod(1).eq(0)
    hours = time.loc[valid_time].floordiv(100).astype(int).value_counts().reindex(range(24), fill_value=0)
    power = frame["frp"].dropna()
    boundaries = [-float("inf"), 10, 50, 100, 500, float("inf")]
    bands = pd.cut(power, bins=boundaries, right=False).value_counts(sort=False)
    quartiles = power.quantile([0.5, 0.9, 0.99]) if len(power) else {}
    return {
        "by_hour": [{"hour": int(hour), "detections": int(count)} for hour, count in hours.items()],
        "by_frp_band": [{"band": index, "detections": int(count)} for index, count in enumerate(bands)],
        "frp_distribution": {
            "samples": int(len(power)),
            "median_mw": float(quartiles[0.5]) if len(power) else None,
            "p90_mw": float(quartiles[0.9]) if len(power) else None,
            "p99_mw": float(quartiles[0.99]) if len(power) else None,
            "max_mw": float(power.max()) if len(power) else None,
        },
    }


def geographic_grid(frame: pd.DataFrame) -> list[list]:
    cells = frame.loc[frame["longitude"].between(-180, 180) & frame["latitude"].between(-90, 90)]
    x = ((cells["longitude"] + 180) * 4).clip(0, 1439).astype(int)
    y = ((90 - cells["latitude"]) * 4).clip(0, 719).astype(int)
    grid = cells.assign(cell=y * 1440 + x).groupby("cell").agg(
        detections=("latitude", "size"), frp_mw=("frp", "sum")
    )
    return [[int(cell), int(count), round(float(power), 2)] for cell, count, power in grid.itertuples(name=None)]


def rank_grid(cells):
    return {
        name: [row[0] for row in nlargest(750, (row for row in cells if row[index] > 0), key=itemgetter(index))]
        for index, name in ((1, "detections"), (2, "frp_mw"))
    }
