from base64 import b64encode
from struct import Struct

import pandas as pd


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


def heat_weight(chunk, metric):
    if metric == "frp":
        return chunk["frp"]
    if metric == "night":
        return chunk["night"]
    if metric == "high":
        return chunk["level"].eq(2)
    return 1
