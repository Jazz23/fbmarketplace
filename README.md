# Facebook Marketplace API

Flask API for scraping Facebook Marketplace data. The project is managed with `uv` and now contains only the API and scraper code.

## Setup

```bash
uv sync
```

Create a `.env` file with optional proxy settings:

```bash
PROXY_LIST_URL=https://proxy.webshare.io/api/v2/proxy/list/download/jxhlgmnyxjhvaaslldboxqxmjhzklvnihxqdftoy/-/any/username/direct/-/?plan_id=13343397
REQUIRE_PROXIES=false
```

`REQUIRE_PROXIES` defaults to `true` when unset.

## Run

```bash
uv run MarketplaceAPI.py
```

## Health Check

```bash
GET /health
```

## Endpoints

### `GET /locations`
Query params: `locationQuery`

### `GET /search`
Query params: `locationLatitude`, `locationLongitude`, `listingQuery`, optional `numPageResults`, `minPrice`, `maxPrice`, `cursor`

### `GET /listing/details`
Query params: `listingID`

### `GET /listing/images`
Query params: `listingID`

### `POST /proxy`
Body: `proxy` or `proxies` (`proxies` can be an object, array, or string)

## Response Shape

```json
{
  "status": "Success",
  "error": {},
  "data": {}
}
```

## Development

```bash
uv run pytest
uv lock
```
