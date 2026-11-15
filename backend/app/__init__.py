from secrets import token_hex

from flask import Flask, jsonify

from .routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(SECRET_KEY=token_hex(32), SESSION_COOKIE_NAME="previa_demo", SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    app.register_blueprint(api, url_prefix="/api")

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": {"code": "invalid_request", "message": error.description}}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": {"code": "not_found", "message": "Rota não encontrada."}}), 404

    @app.errorhandler(503)
    def data_unavailable(error):
        return jsonify({"error": {"code": "service_unavailable", "message": error.description}}), 503

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": {"code": "internal_error", "message": "Não foi possível consultar os dados."}}), 500

    return app
