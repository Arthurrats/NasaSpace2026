import math

import numpy as np
import pandas as pd


MARKER_LIMIT = 480
LEVEL_NAMES = ("low", "medium", "high")


def sample_markers(points: pd.DataFrame) -> list[list]:
    # Sample uniformly from observations while preserving their coordinates.
    selected = points.sample(n=min(len(points), MARKER_LIMIT), random_state=17)
    return [
        [f"point:{index}", round(lng, 6), round(lat, 6), LEVEL_NAMES[level], 1]
        for index, lng, lat, level in selected.itertuples(name=None)
    ]


def cluster_markers(points: pd.DataFrame, longitude: pd.Series) -> list[list]:
    latitude = points["latitude"]
    cosine = max(0.15, math.cos(math.radians(float(latitude.median()))))
    x = (longitude - longitude.min()) * cosine
    y = latitude - latitude.min()
    span = max(float(x.max()), float(y.max()), 1e-9)
    x, y = x / span, y / span

    # Tiny buckets speed up neighbor searches. Each representative is an observed point.
    resolution = 112
    bucket = (y * resolution).astype(int) * (resolution + 1) + (x * resolution).astype(int)
    priority = np.random.default_rng(17).random(len(points))
    groups = points.assign(bucket=bucket, priority=priority).groupby("bucket")
    stats = groups.agg(representative=("priority", "idxmax"), count=("level", "size"), level=("level", "max"))
    reps = stats["representative"].to_numpy()
    counts = stats["count"].to_numpy()
    levels = stats["level"].to_numpy()
    seed_order = np.lexsort((-priority[reps], -counts))
    rx, ry = x.to_numpy()[reps], y.to_numpy()[reps]
    observed = points[["longitude", "latitude"]].to_numpy()[reps]
    radius = 0.026

    while True:
        remaining = np.ones(len(reps), dtype=bool)
        data = []
        for seed in seed_order:
            if not remaining[seed]:
                continue
            neighbors = remaining & (((rx - rx[seed]) ** 2 + (ry - ry[seed]) ** 2) <= radius ** 2)
            remaining[neighbors] = False
            lng, lat = observed[seed]
            data.append([
                f"group:{int(reps[seed])}", round(float(lng), 6), round(float(lat), 6),
                LEVEL_NAMES[levels[neighbors].max()], int(counts[neighbors].sum()),
            ])
            if len(data) > MARKER_LIMIT:
                break
        if len(data) <= MARKER_LIMIT:
            return data
        radius *= 1.25
