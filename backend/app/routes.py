from flask import Blueprint

api = Blueprint("api", __name__)


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
