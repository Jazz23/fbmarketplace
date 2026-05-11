# Facebook Marketplace API

Flask API for scraping Facebook Marketplace data. The project is managed with `uv` and now contains only the API and scraper code.

## Setup

```bash
uv sync
```

## Run

```bash
uv run python MarketplaceAPI.py
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
Body: `proxy` or `proxies`

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
