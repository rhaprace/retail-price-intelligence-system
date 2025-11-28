# API Package

REST API for Retail Price Intelligence System built with FastAPI.

## Structure

- **`main.py`**: FastAPI application and route registration
- **`routes/`**: Individual route modules
  - `products.py`: Product endpoints
  - `prices.py`: Price endpoints
  - `sources.py`: Source endpoints
  - `comparisons.py`: Price comparison endpoints
  - `alerts.py`: Price alert endpoints
  - `analytics.py`: Analytics endpoints

## Running the API

```bash
uvicorn api.main:app --reload

uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Products

- `GET /api/products/` - List products (with filters: category, brand, search)
- `GET /api/products/{product_id}` - Get product by ID
- `POST /api/products/` - Create product
- `GET /api/products/{product_id}/sources` - Get sources for product
- `GET /api/products/{product_id}/prices` - Get price history for product

### Prices

- `GET /api/prices/latest` - Get latest prices
- `GET /api/prices/product-source/{product_source_id}` - Get price history
- `GET /api/prices/product-source/{product_source_id}/latest` - Get latest price
- `GET /api/prices/product-source/{product_source_id}/metrics` - Get price metrics

### Sources

- `GET /api/sources/` - List all sources
- `GET /api/sources/{source_id}` - Get source by ID
- `POST /api/sources/` - Create source

### Comparisons

- `GET /api/comparisons/` - Get price comparisons
- `GET /api/comparisons/product/{product_id}` - Get comparison for product

### Alerts

- `GET /api/alerts/` - List alerts
- `GET /api/alerts/{alert_id}` - Get alert by ID
- `POST /api/alerts/` - Create alert
- `PATCH /api/alerts/{alert_id}/activate` - Activate alert
- `PATCH /api/alerts/{alert_id}/deactivate` - Deactivate alert
- `DELETE /api/alerts/{alert_id}` - Delete alert

### Analytics

- `GET /api/analytics/discounts` - Get discount analysis
- `GET /api/analytics/discounts/fake` - Get fake discounts
- `GET /api/analytics/discounts/product-source/{product_source_id}` - Get analysis for product-source

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Requests

### Get Products

```bash
curl http://localhost:8000/api/products/?category=Electronics&limit=10
```

### Get Price History

```bash
curl http://localhost:8000/api/prices/product-source/1?days=30
```

### Create Alert

```bash
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "123e4567-e89b-12d3-a456-426614174000",
    "target_price": 99.99,
    "is_active": true
  }'
```

### Get Fake Discounts

```bash
curl http://localhost:8000/api/analytics/discounts/fake?limit=50
```

## Query Parameters

Common query parameters:
- `skip`: Pagination offset (default: 0)
- `limit`: Number of results (default: 100, max: 1000)
- `days`: Number of days for historical data (default: 30)

## Response Format

All endpoints return JSON. Successful responses include:
- Data objects or arrays
- Standard HTTP status codes (200, 201, 404, 400, etc.)

Error responses:
```json
{
  "detail": "Error message"
}
```

