import numpy as np
import pandas as pd

from .metrics import valid_frp


SOUTH_AMERICA = (-84, -57, -31, 15)
WEEK = 7
TRAINING_DAYS = 28
HORIZON = 14


def weekday_forecast(history, horizon):
    recent = history[-TRAINING_DAYS:].reshape(-1, WEEK)
    return np.resize(recent.mean(axis=0), horizon)


def project_daily(counts, last_date):
    if not counts.any():
        return None

    estimated = weekday_forecast(counts, HORIZON)
    # Each origin uses only days available before the forecast. Compare like horizons.
    errors = np.array([
        counts[origin:origin + HORIZON] - weekday_forecast(counts[:origin], HORIZON)
        for origin in range(max(TRAINING_DAYS, len(counts) - 56), len(counts) - HORIZON + 1)
    ])
    lower, upper = np.quantile(errors, [.1, .9], axis=0)
    dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=HORIZON)
    return {
        "mae": round(float(np.abs(errors).mean()), 1),
        "training_days": TRAINING_DAYS,
        "evaluation_windows": len(errors),
        "days": [
            {
                "date": date.date().isoformat(),
                "estimate": round(float(value)),
                "lower": max(0, round(float(value + min(0, low)))),
                "upper": round(float(value + max(0, high))),
            }
            for date, value, low, high in zip(dates, estimated, lower, upper)
        ],
    }


def monthly_detections(frame):
    return frame.groupby(frame["acq_date"].dt.month).size().reindex(range(1, 13), fill_value=0)


def summarize_activity(frame, year, available_years, history):
    first = f"{year}-01-01"
    last = f"{year}-12-31"
    dates = pd.date_range(first, last, tz="UTC")
    west, south, east, north = SOUTH_AMERICA
    daily = frame.assign(frp_mw=valid_frp(frame["frp"])).groupby("acq_date").agg(
        detections=("acq_date", "size"), frp_mw=("frp_mw", "sum"),
    ).reindex(dates, fill_value=0)

    count = daily["detections"]
    reference = count.shift(1).rolling(TRAINING_DAYS, min_periods=14)
    upper = reference.quantile(.90)
    # With mostly empty days, use a minimum of two detections for a high flag.
    daily["unusual"] = (count > upper) & (count >= 2)
    monthly_peak = count.groupby(daily.index.month).transform("max").clip(lower=1)
    daily["intensity_level"] = np.ceil(count * 4 / monthly_peak).astype(int)
    days = [
        {"date": date.date().isoformat(), "detections": int(total), "frp_mw": round(power, 2),
         "unusual": bool(flag), "intensity_level": int(level)}
        for date, total, power, flag, level in daily.itertuples()
    ]

    grouped = daily.groupby(daily.index.month)
    totals = grouped.agg(detections=("detections", "sum"), days=("detections", "size"), unusual_days=("unusual", "sum"))
    peaks = grouped["detections"].idxmax()
    totals["rate"] = totals["detections"] / totals["days"]
    # Highlight up to three months with the most detections per day in this archive.
    critical = totals.loc[totals["rate"] > 0, "rate"].nlargest(3).index
    average = pd.DataFrame(history).mean(axis=1) if len(history) >= 2 else None
    months = []
    for month, total, length, unusual_days, rate in totals.itertuples():
        baseline = float(average.loc[month]) if average is not None else None
        delta = total - baseline if baseline is not None else None
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-{length:02d}"
        months.append({
            "month": int(month), "detections": int(total), "daily_average": round(rate, 2),
            "critical": month in critical, "reported_incidents": None,
            "start_date": start, "end_date": end, "peak_date": peaks.loc[month].date().isoformat(),
            "unusual_days": int(unusual_days),
            "baseline_average": round(baseline, 2) if baseline is not None else None,
            "anomaly": round(delta, 2) if delta is not None else None,
            "anomaly_pct": round(100 * delta / baseline, 2) if baseline else None,
        })

    bounds = None
    if not frame.empty:
        min_lon, max_lon = frame["longitude"].agg(["min", "max"])
        min_lat, max_lat = frame["latitude"].agg(["min", "max"])
        bounds = [[max(west, float(min_lon) - 1), max(south, float(min_lat) - 1)],
                  [min(east, float(max_lon) + 1), min(north, float(max_lat) + 1)]]

    return {
        "year": year, "first_date": first, "last_date": last,
        "available_years": available_years, "baseline_years": sorted(history) if average is not None else [],
        "total_detections": int(count.sum()), "reported_incidents": None,
        "bounds": bounds, "days": days, "months": months,
        "forecast": project_daily(count.to_numpy(), dates[-1]),
        "seasonal": {
            "year": year + 1, "reference_year": year, "method": "seasonal_naive",
            "months": [{"month": row["month"], "estimate": row["detections"],
                        "reference_start_date": row["start_date"], "reference_end_date": row["end_date"]} for row in months],
        },
    }
