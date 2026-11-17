from flask import abort, request

from ..analysis.activity import SOUTH_AMERICA, monthly_detections, summarize_activity
from ..data.archive import archive_partitions, archive_revision
from ..data.map_index import activity_frame
from ..response_cache import cached_response
from . import api
from .filters import map_sources, requested_map_bbox


@api.get("/activity")
@cached_response(archive_revision)
def fire_activity() -> tuple[dict, int]:
    sensors, countries = map_sources()
    west, south, east, north = requested_map_bbox(SOUTH_AMERICA, allow_wrap=False)
    scope_west, scope_south, scope_east, scope_north = SOUTH_AMERICA
    bounds = max(west, scope_west), max(south, scope_south), min(east, scope_east), min(north, scope_north)
    partitions = {(sensor, country) for sensor in sensors for country in countries}
    available_years = sorted(year for year, sources in archive_partitions().items() if partitions <= sources)
    if not available_years:
        abort(503, description="Não há um ano com arquivos para todos os sensores e países do recorte.")

    try:
        year = int(request.args.get("year", available_years[-1]))
    except ValueError:
        abort(400, description="year deve ser um ano inteiro.")
    if year not in available_years:
        abort(400, description="O ano não está disponível para todos os sensores e países do recorte.")

    past = [previous for previous in available_years if previous < year]
    history = {previous: monthly_detections(activity_frame(previous, partitions, bounds)) for previous in past} if len(past) >= 2 else {}
    return summarize_activity(activity_frame(year, partitions, bounds), year, available_years, history), 200
