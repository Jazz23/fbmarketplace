from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import MarketplaceAPI
import MarketplaceScraper


def test_health_endpoint():
    client = MarketplaceAPI.create_app().test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_locations_requires_query():
    client = MarketplaceAPI.create_app().test_client()

    response = client.get("/locations")

    assert response.status_code == 400
    assert response.get_json()["error"]["source"] == "User"


def test_search_delegates_to_scraper(monkeypatch):
    client = MarketplaceAPI.create_app().test_client()

    def fake_get_listings(**kwargs):
        assert kwargs["locationLatitude"] == "29.7602"
        assert kwargs["locationLongitude"] == "-95.3694"
        assert kwargs["listingQuery"] == "couch"
        return "Success", {}, {"listingPages": [], "page_info": {"end_cursor": None, "has_next_page": False}}

    monkeypatch.setattr(MarketplaceScraper, "getListings", fake_get_listings)

    response = client.get(
        "/search",
        query_string={
            "locationLatitude": "29.7602",
            "locationLongitude": "-95.3694",
            "listingQuery": "couch",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["listingPages"] == []
