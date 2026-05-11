from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Blueprint, Flask, jsonify, request

def _load_dotenv(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

import MarketplaceScraper


api = Blueprint("api", __name__)


def build_response(status: str, error: dict[str, Any], data: dict[str, Any], http_status: int = 200):
    return jsonify({
        "status": status,
        "error": error,
        "data": data,
    }), http_status


def missing_param(message: str = "Missing required parameter"):
    return build_response("Failure", {
        "source": "User",
        "message": message,
    }, {}, 400)


def _http_status(status: str, error: dict[str, Any]) -> int:
    if status == "Success":
        return 200
    if error.get("source") == "User":
        return 400
    if error.get("source") == "Parsing":
        return 500
    return 502


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.get("/locations")
def locations():
    locationQuery = request.args.get("locationQuery")

    if not locationQuery:
        return missing_param()

    status, error, data = MarketplaceScraper.getLocations(locationQuery=locationQuery)
    return build_response(status, error, data, _http_status(status, error))


@api.get("/search")
def search():
    locationLatitude = request.args.get("locationLatitude")
    locationLongitude = request.args.get("locationLongitude")
    listingQuery = request.args.get("listingQuery")
    minPrice = request.args.get("minPrice")
    maxPrice = request.args.get("maxPrice")
    cursor = request.args.get("cursor")

    try:
        numPageResults = int(request.args.get("numPageResults", 1))
    except ValueError:
        numPageResults = 1

    if not (locationLatitude and locationLongitude and listingQuery):
        return missing_param("Missing required parameter(s)")

    status, error, data = MarketplaceScraper.getListings(
        locationLatitude=locationLatitude,
        locationLongitude=locationLongitude,
        listingQuery=listingQuery,
        numPageResults=numPageResults,
        minPrice=minPrice,
        maxPrice=maxPrice,
        cursor=cursor,
    )

    return build_response(status, error, data, _http_status(status, error))


@api.get("/listing/details")
def listing_details():
    listingID = request.args.get("listingID")

    if not listingID:
        return missing_param()

    status, error, data = MarketplaceScraper.getListingDetails(listingID)
    return build_response(status, error, data, _http_status(status, error))


@api.get("/listing/images")
def listing_images():
    listingID = request.args.get("listingID")

    if not listingID:
        return missing_param()

    status, error, data = MarketplaceScraper.getListingImages(listingID)
    return build_response(status, error, data, _http_status(status, error))


@api.post("/proxy")
def proxy():
    payload = request.get_json(silent=True) or {}
    proxy_url = payload.get("proxy") or request.args.get("proxy")
    proxies = payload.get("proxies")

    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}

    if proxies is None:
        return missing_param("Missing required parameter(s)")

    if not isinstance(proxies, (dict, list, str)):
        return build_response("Failure", {
            "source": "User",
            "message": "proxies must be an object, array, or proxy must be a string",
        }, {}, 400)

    MarketplaceScraper.update_session_proxy(proxies)
    return build_response("Success", {}, {"proxies": proxies})


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(api)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({
            "status": "Failure",
            "error": {"source": "User", "message": "Route not found"},
            "data": {},
        }), 404

    return app


app = create_app()


def main() -> None:
    MarketplaceScraper.configure_proxy_session_from_env()

    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )


if __name__ == "__main__":
    main()
