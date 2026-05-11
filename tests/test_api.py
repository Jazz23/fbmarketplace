from __future__ import annotations

import os
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


def test_configure_proxy_session_from_env(monkeypatch):
    monkeypatch.setenv("PROXY_LIST_URL", "https://example.com/proxies.txt")
    monkeypatch.setenv("REQUIRE_PROXIES", "true")

    class FakeResponse:
        status_code = 200
        text = "127.0.0.1:8080:user:pass\nhttps://user:pass@127.0.0.2:8081\n"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(MarketplaceScraper.requests, "get", lambda *args, **kwargs: FakeResponse())

    MarketplaceScraper.configure_proxy_session_from_env()

    assert MarketplaceScraper.SCRAPER_SESSION.proxies["http"].startswith("http://")
    assert "@" in MarketplaceScraper.SCRAPER_SESSION.proxies["http"]


def test_update_session_proxy_cycles_through_pool():
    first = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
    second = {"http": "http://127.0.0.2:8080", "https": "http://127.0.0.2:8080"}

    MarketplaceScraper.update_session_proxy([first, second])

    assert MarketplaceScraper.SCRAPER_SESSION.proxies == first

    MarketplaceScraper._apply_next_proxy()
    assert MarketplaceScraper.SCRAPER_SESSION.proxies == first

    MarketplaceScraper._apply_next_proxy()
    assert MarketplaceScraper.SCRAPER_SESSION.proxies == second

    MarketplaceScraper._apply_next_proxy()
    assert MarketplaceScraper.SCRAPER_SESSION.proxies == first


def test_proxy_endpoint_accepts_proxy_list():
    client = MarketplaceAPI.create_app().test_client()

    response = client.post(
        "/proxy",
        json={
            "proxies": [
                {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"},
                {"http": "http://127.0.0.2:8080", "https": "http://127.0.0.2:8080"},
            ]
        },
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["proxies"][0]["http"] == "http://127.0.0.1:8080"


def test_proxy_test_endpoint_reports_proxy_and_ip(monkeypatch):
    client = MarketplaceAPI.create_app().test_client()

    MarketplaceScraper.update_session_proxy({"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"})

    class FakeResponse:
        text = "203.0.113.9\n"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(MarketplaceScraper.SCRAPER_SESSION, "get", lambda *args, **kwargs: FakeResponse())

    response = client.get("/proxy/test")

    assert response.status_code == 200
    assert response.get_json()["data"] == {"proxy": "127.0.0.1:8080", "internet_ip": "203.0.113.9"}
