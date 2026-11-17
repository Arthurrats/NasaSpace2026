import os
from secrets import token_hex

from flask import Flask, abort, jsonify, request
from werkzeug.exceptions import HTTPException

# As importações registram os endpoints no blueprint compartilhado.
from .api import api, activity, map, observations, summary, system
from .maps.territories import MAX_BODY


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("PREVIA_SECRET_KEY") or token_hex(32),
        SESSION_COOKIE_NAME="previa_demo",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("PREVIA_SECURE_COOKIE") == "1",
        MAX_CONTENT_LENGTH=MAX_BODY,
    )
    app.register_blueprint(api, url_prefix="/api")

    @app.before_request
    def validate_request():
        if len(request.query_string) > 2048:
            abort(414)
        if any(len(values) > 1 for _, values in request.args.lists()):
            abort(400, description="Cada parâmetro deve ser informado apenas uma vez.")
        if request.endpoint in {"api.demo_session", "api.map_territory"} and request.method in {"POST", "DELETE"}:
            if request.headers.get("Sec-Fetch-Site") == "cross-site":
                abort(403)
            if request.method == "POST" and not request.is_json:
                abort(415)

    @app.after_request
    def secure_response(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        if response.status_code >= 400:
            response.cache_control.no_store = True
        return response

    @app.errorhandler(HTTPException)
    def api_error(error):
        code, message = {
            400: ("invalid_request", error.description),
            403: ("forbidden", "Origem da requisição não permitida."),
            404: ("not_found", "Rota ou recurso não encontrado."),
            405: ("method_not_allowed", "Método não permitido."),
            413: ("payload_too_large", "O corpo da requisição excede o limite."),
            414: ("uri_too_long", "A consulta excede o limite."),
            415: ("unsupported_media_type", "Envie a solicitação em JSON."),
            500: ("internal_error", "Não foi possível consultar os dados."),
            503: ("service_unavailable", error.description),
        }.get(error.code, ("request_failed", "Não foi possível atender à requisição."))
        response = error.get_response()
        response.set_data(app.json.dumps({"error": {"code": code, "message": message}}))
        response.mimetype = "application/json"
        return response

    return app


app = create_app()
