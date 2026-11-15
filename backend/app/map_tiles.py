import math
from io import BytesIO

import numpy as np
from PIL import Image, ImageColor, ImageDraw


TILE_SIZE = 256
PAD = 16
OVERSAMPLE = 2
COLORS = ["#b6e36b", "#ff8a32", "#e84b32"]
HEAT_REFERENCE = {"detections": 120, "frp": 2400, "night": 120, "high": 120}
HEAT_PALETTES = {
    "default": ([0, 0.28, 0.54, 1], [ImageColor.getrgb(color) for color in ["#78c850", *COLORS]]),
    # Samples from the Cividis ramp, Nuñez et al. (2018), doi:10.1371/journal.pone.0199239.
    "accessible": ([index / 8 for index in range(9)], [ImageColor.getrgb(color) for color in (
        "#00224e", "#1a386f", "#434e6c", "#61656f", "#7d7c78", "#9a9376", "#bbad6d", "#ddc858", "#fee838",
    )]),
}
MERCATOR_LIMIT = 85.0511287798066


def tile_edges(zoom: int, column: int, row: int, padding: int = 0) -> tuple:
    world = (1 << zoom) * TILE_SIZE

    def longitude(x):
        return x * 360 / world - 180

    def latitude(y):
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / world))))

    return (
        longitude(column * TILE_SIZE - padding),
        max(-MERCATOR_LIMIT, latitude((row + 1) * TILE_SIZE + padding)),
        longitude((column + 1) * TILE_SIZE + padding),
        min(MERCATOR_LIMIT, latitude(row * TILE_SIZE - padding)),
    )


def project_tile(longitude, latitude, zoom: int, column: int, row: int) -> tuple:
    world = (1 << zoom) * TILE_SIZE
    x = (np.asarray(longitude) + 180) / 360 * world
    y = (1 - np.arcsinh(np.tan(np.radians(np.clip(latitude, -MERCATOR_LIMIT, MERCATOR_LIMIT)))) / np.pi) * world / 2
    # The tile edges at the antimeridian overlap the other side of the world.
    x += np.round((column * TILE_SIZE + TILE_SIZE / 2 - x) / world) * world
    return x - column * TILE_SIZE, y - row * TILE_SIZE


def encode_tile(image, scale=1):
    origin = PAD * scale
    end = origin + TILE_SIZE * scale
    buffer = BytesIO()
    image.crop((origin, origin, end, end)).save(buffer, format="PNG", compress_level=3)
    return buffer.getvalue()


def blur_heat(density, axis, radius):
    padded = np.moveaxis(density, axis, -1)
    padding = [(0, 0)] * (padded.ndim - 1) + [(radius + 1, radius)]
    cumulative = np.pad(padded, padding).cumsum(axis=-1)
    diameter = radius * 2 + 1
    average = (cumulative[..., diameter:] - cumulative[..., :-diameter]) / diameter
    return np.moveaxis(average, -1, axis)


def render_heat_tile(zoom, column, row, longitude, latitude, weight, metric, palette="default", days=365):
    x, y = project_tile(longitude, latitude, zoom, column, row)
    side = TILE_SIZE + 2 * PAD
    cx = np.floor(x + PAD).astype(int)
    cy = np.floor(y + PAD).astype(int)
    valid = (cx >= 0) & (cx < side) & (cy >= 0) & (cy < side)
    weight = np.asarray(weight, dtype=float)[valid]
    if not np.any(weight > 0):
        return encode_tile(Image.new("RGBA", (side, side)))

    density = np.bincount(cy[valid] * side + cx[valid], weights=weight, minlength=side ** 2).reshape(side, side)
    radius = 6
    for _ in range(2):
        density = blur_heat(blur_heat(density, 0, radius), 1, radius)

    # At each zoom, all tiles share a scale. A pixel covers four times more area one zoom out.
    reference = HEAT_REFERENCE[metric] * max(1 / 30, 4 ** (6 - zoom)) * max(.10, min(1, math.sqrt(days / 365)))
    neighborhood = np.maximum(density, 0) * (radius * 2 + 1) ** 2
    relative = np.log1p(24 * neighborhood / reference) / math.log(25)
    relative = np.minimum(relative, 1)
    offsets, rgb = HEAT_PALETTES[palette]
    alpha = np.sqrt(relative) * 218
    channels = [np.interp(relative, offsets, channel) for channel in zip(*rgb)]
    return encode_tile(Image.fromarray(np.stack([*channels, alpha], axis=-1).astype(np.uint8)))


def render_tile(mode: str, zoom: int, column: int, row: int, longitude, latitude, level) -> bytes:
    x, y = project_tile(longitude, latitude, zoom, column, row)
    side = (TILE_SIZE + 2 * PAD) * OVERSAMPLE
    image = Image.new("RGBA", (side, side))
    draw = ImageDraw.Draw(image)
    radius = {"cluster": 7, "circle": 4, "pixel": 2.5, "dots": 1}[mode]
    valid = (x >= -PAD) & (x <= TILE_SIZE + PAD) & (y >= -PAD) & (y <= TILE_SIZE + PAD)
    cx = np.rint((x[valid] + PAD) * OVERSAMPLE).astype(int)
    cy = np.rint((y[valid] + PAD) * OVERSAMPLE).astype(int)
    r = round(radius * OVERSAMPLE)
    if mode == "dots":
        # Plot every occupied position at half-pixel precision without sampling observations.
        cells = np.unique(cx + (side + 1) * cy)
        for cell in cells:
            py, px = divmod(int(cell), side + 1)
            draw.ellipse((px - r, py - r, px + r - 1, py + r - 1), fill="#fee838e0")
        return encode_tile(image, OVERSAMPLE)

    level = np.asarray(level, dtype=np.int64)[valid]
    if mode != "cluster" and len(cx):
        # Coincident raster pixels have identical glyphs. Draw once for each color.
        key = cx + (side + 1) * cy + (side + 1) ** 2 * level
        _, keep = np.unique(key, return_index=True)
        cx, cy, level = cx[keep], cy[keep], level[keep]
    for index, color in enumerate(COLORS):
        matches = level == index
        for px, py in zip(cx[matches], cy[matches]):
            box = (int(px - r), int(py - r), int(px + r - 1), int(py + r - 1))
            if mode == "pixel":
                draw.rectangle(box, fill=color)
            else:
                draw.ellipse(box, fill=color, outline="#101b19", width=OVERSAMPLE)
    return encode_tile(image, OVERSAMPLE)
