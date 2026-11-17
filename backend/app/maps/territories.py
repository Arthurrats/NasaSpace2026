import json
import os
import re
from collections import OrderedDict
from hashlib import sha256
from threading import Lock
from zlib import compress, decompress

import numpy as np
from flask import abort
from PIL import Image
from redis.exceptions import RedisError
from shapely import from_geojson, get_coordinates, intersects_xy, prepare, transform
from shapely.errors import GEOSException

from ..response_cache import redis_client
from .tiles import TILE_SIZE


MAX_BODY = 8 * 1024 * 1024
_territories = OrderedDict()
_lock = Lock()


class Territory:
    def __init__(self, geometry, seam=None):
        self.seam = seam
        if seam is not None:
            geometry = transform(geometry, lambda x, y: (self.unwrap(x), y), interleaved=False)
        if not geometry.is_valid:
            geometry = geometry.buffer(0)
        if geometry.is_empty or not geometry.area:
            raise ValueError("Contorno sem área.")
        self.geometry = geometry
        prepare(geometry)
        west, south, east, north = geometry.bounds
        self.bounds = (west - 360 if west >= 180 and east > 180 else west, south,
                       east - 360 if east > 180 else east, north)

    def unwrap(self, longitude):
        return np.where(longitude < self.seam, longitude + 360, longitude)

    def covers(self, longitude, latitude):
        x = np.asarray(longitude)
        return intersects_xy(self.geometry, self.unwrap(x) if self.seam is not None else x, np.asarray(latitude))

    def clip_tile(self, zoom, column, row, image):
        alpha = np.array(image.getchannel("A"))
        y, x = np.nonzero(alpha)
        if not len(x):
            return image
        scale = TILE_SIZE / image.width
        world = (1 << zoom) * TILE_SIZE
        lon = ((column * TILE_SIZE + (x + .5) * scale) / world) * 360 - 180
        lat = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * (row * TILE_SIZE + (y + .5) * scale) / world))))
        outside = ~self.covers(lon, lat)
        alpha[y[outside], x[outside]] = 0
        image.putalpha(Image.fromarray(alpha))
        return image


def _parse(body):
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError("Contorno inválido.")
    seam = payload.get("seam")
    if seam is not None and (type(seam) not in {int, float} or not -180 < seam < 180):
        raise ValueError("Meridiano inválido.")
    raw = payload.get("geometry")
    if not isinstance(raw, dict) or raw.get("type") not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Tipo de contorno inválido.")
    geometry = from_geojson(json.dumps(raw))
    coordinates = get_coordinates(geometry)
    if not 3 < len(coordinates) <= 250_000 or not (np.abs(coordinates) <= [180, 90]).all():
        raise ValueError("Coordenadas inválidas.")
    return Territory(geometry, seam)


def _remember(key, territory):
    with _lock:
        _territories[key] = territory
        _territories.move_to_end(key)
        if len(_territories) > 16:
            _territories.popitem(last=False)


def _cache():
    url = os.environ.get("PREVIA_REDIS_URL")
    return redis_client(url) if url else None


def register_territory(body):
    key = sha256(body).hexdigest()
    try:
        territory = _parse(body)
    except (ValueError, TypeError, OverflowError, RecursionError, GEOSException):
        abort(400, description="O contorno do território é inválido.")
    _remember(key, territory)
    cache = _cache()
    if cache is not None:
        try:
            cache.set("previa:territory:" + key, compress(body, 1), ex=3600)
        except RedisError:
            pass
    return key


def get_territory(key):
    if key is None:
        return None
    if not re.fullmatch(r"[0-9a-f]{64}", key):
        abort(400, description="Identificador de território inválido.")
    with _lock:
        territory = _territories.get(key)
        if territory is not None:
            _territories.move_to_end(key)
            return territory
    cache = _cache()
    if cache is not None:
        try:
            body = cache.get("previa:territory:" + key)
        except RedisError:
            body = None
        if body is not None:
            territory = _parse(decompress(body))
            _remember(key, territory)
            return territory
    abort(404, description="O contorno precisa ser enviado novamente.")
