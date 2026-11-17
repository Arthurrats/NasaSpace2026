from flask import abort, request

from ..data.archive import dataset_revision
from ..models.detection import Detection
from ..models.pagination import Pagination
from ..response_cache import cached_response
from . import api
from .filters import query_frame


def pagination() -> tuple[int, int]:
    try:
        limit = int(request.args.get("limit", "1000"))
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        abort(400, description="limit e offset devem ser inteiros.")
    if not 1 <= limit <= 5000 or offset < 0:
        abort(400, description="limit deve estar entre 1 e 5000 e offset não pode ser negativo.")
    return limit, offset


@api.get("/fires")
@cached_response(dataset_revision)
def fires() -> tuple[dict, int]:
    limit, offset = pagination()
    frame = query_frame().sort_values(["acq_date", "acq_time"], ascending=False)
    total = len(frame)
    selected = frame.iloc[offset:offset + limit] if offset < total else frame.iloc[:0]
    return {
        "data": [Detection.from_archive_row(row).to_payload() for row in selected.to_dict(orient="records")],
        "pagination": Pagination(limit=limit, offset=offset, total=total).to_payload(),
        "meta": {"synthetic": False, "sensors": sorted(frame["sensor"].unique().tolist()), "unit": "satellite detections"},
    }, 200
