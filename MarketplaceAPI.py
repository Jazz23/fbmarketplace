from flask import Flask, request
import MarketplaceScraper

API = Flask(__name__)


def build_response(status, error, data):
    return {
        "status": status,
        "error": error,
        "data": data,
    }


def missing_param(message="Missing required parameter"):
    return build_response("Failure", {
        "source": "User",
        "message": message,
    }, {})


@API.route("/locations", methods=["GET"])
def locations():
    locationQuery = request.args.get("locationQuery")

    if not locationQuery:
        return missing_param()

    status, error, data = MarketplaceScraper.getLocations(locationQuery=locationQuery)
    return build_response(status, error, data)


@API.route("/search", methods=["GET"])
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

    return build_response(status, error, data)


@API.route("/listing/details", methods=["GET"])
def listing_details():
    listingID = request.args.get("listingID")

    if not listingID:
        return missing_param()

    status, error, data = MarketplaceScraper.getListingDetails(listingID)
    return build_response(status, error, data)


@API.route("/listing/images", methods=["GET"])
def listing_images():
    listingID = request.args.get("listingID")

    if not listingID:
        return missing_param()

    status, error, data = MarketplaceScraper.getListingImages(listingID)
    return build_response(status, error, data)


@API.route("/proxy", methods=["POST"])
def proxy():
    payload = request.get_json(silent=True) or {}
    proxy_url = payload.get("proxy") or request.args.get("proxy")
    proxies = payload.get("proxies")

    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}

    if proxies is None:
        return missing_param("Missing required parameter(s)")

    if not isinstance(proxies, dict):
        return build_response("Failure", {
            "source": "User",
            "message": "proxies must be an object or proxy must be a string",
        }, {})

    MarketplaceScraper.update_session_proxy(proxies)
    return build_response("Success", {}, {"proxies": proxies})

if __name__ == "__main__":
    API.run(debug=True)
