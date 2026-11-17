from flask import abort, jsonify, request, session

from ..data.archive import COUNTRIES, COUNTRY_ISO3
from . import api


@api.get("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@api.route("/demo-session", methods=["GET", "POST", "DELETE"])
def demo_session():
    if request.method == "POST":
        request.max_content_length = 1024
        if not isinstance(request.get_json(), dict):
            abort(400, description="Envie um objeto JSON.")
        session["demo"] = True
    elif request.method == "DELETE":
        session.pop("demo", None)
    response = jsonify(active=session.get("demo", False))
    response.cache_control.no_store = True
    return response


@api.get("/countries")
def countries() -> tuple[dict, int]:
    return {"countries": [{"id": COUNTRIES[name], "name": name, "iso3": COUNTRY_ISO3[name]} for name in COUNTRIES]}, 200
