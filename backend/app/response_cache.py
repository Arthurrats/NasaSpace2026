import hashlib
import json
import os
from functools import lru_cache, wraps
from pathlib import Path

from flask import current_app, make_response, request
from redis import Redis
from redis.backoff import NoBackoff
from redis.exceptions import RedisError
from redis.retry import Retry


def file_revision(path: Path) -> tuple:
    try:
        info = path.stat()
    except FileNotFoundError:
        return (str(path), None)
    return str(path), info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_ino


@lru_cache(maxsize=1)
def application_revision() -> str:
    root = Path(__file__).parent
    source = b"".join(path.read_bytes() for path in sorted(root.glob("*.py")))
    return hashlib.sha256(source).hexdigest()


@lru_cache(maxsize=1)
def redis_client(url: str) -> Redis:
    return Redis.from_url(url, socket_connect_timeout=0.3, socket_timeout=0.3, retry=Retry(NoBackoff(), 0))


def cached_response(dataset_revision, *, mimetype="application/json", max_age=None):
    def decorate(view):
        @wraps(view)
        def serve(*args, **kwargs):
            revision = dataset_revision()
            key_parts = (application_revision(), request.path, sorted(request.args.lists()), revision)
            digest = hashlib.sha256(json.dumps(key_parts).encode()).hexdigest()
            key = "previa:response:" + digest
            url = os.environ.get("PREVIA_REDIS_URL")
            cache = None
            body = None
            if url:
                try:
                    cache = redis_client(url)
                    body = cache.get(key)
                except RedisError:
                    cache = None
                    current_app.logger.debug("Redis unavailable; calculating response from Parquet.")

            if body is None:
                response = make_response(view(*args, **kwargs))
                if response.status_code != 200:
                    return response
                body = response.get_data()
                if revision != dataset_revision():
                    response.cache_control.no_store = True
                    return response
                if cache is not None:
                    try:
                        cache.set(key, body, ex=1800)
                    except RedisError:
                        current_app.logger.debug("Redis did not store response.")
            else:
                response = current_app.response_class(body, mimetype=mimetype)

            response.set_etag(hashlib.sha256(body).hexdigest())
            response.cache_control.private = True
            if max_age is None:
                response.cache_control.no_cache = True
            else:
                response.cache_control.max_age = max_age
            return response.make_conditional(request)
        return serve
    return decorate
