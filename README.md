# Retail Price Intelligence System

Track, compare, and analyze product prices across e-commerce platforms.

## Quick Start

### Docker (Recommended)

```bash
# 1. Configure environment
cp env.example .env
# Edit .env: set DB_PASSWORD and JWT_SECRET_KEY

# 2. Start services
docker-compose up -d

# 3. Access API
open http://localhost:8000/docs
```

### Local Development

```bash
# 1. Install dependencies
cd server
pip install -r requirements.txt

# 2. Configure environment
cp ../env.example ../.env
# Edit .env with your database credentials

# 3. Setup database
python setup_database.py

# 4. Run API
python run_api.py
```

**API available at:** http://localhost:8000/docs

## Project Structure

```
├── client/                 # Frontend (React/Next.js)
├── server/                 # Backend API
│   ├── api/               # FastAPI routes
│   ├── models/            # SQLAlchemy + Pydantic
│   ├── scrapers/          # E-commerce scrapers
│   ├── pipeline/          # Analytics tasks
│   ├── database/          # Schema + migrations
│   └── tests/             # Test suite
├── docker-compose.yml
└── env.example
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/products/` | GET | List products |
| `/api/products/{id}` | GET | Product details |
| `/api/prices/latest` | GET | Latest prices |
| `/api/prices/product-source/{id}` | GET | Price history |
| `/api/comparisons/` | GET | Price comparisons |
| `/api/alerts/` | GET/POST | Manage price alerts |
| `/api/analytics/discounts/fake` | GET | Detect fake discounts |

Full documentation at `/docs` when running.

## Configuration

Required environment variables:

| Variable | Description |
|----------|-------------|
| `DB_PASSWORD` | PostgreSQL password |
| `JWT_SECRET_KEY` | Auth secret (generate: `openssl rand -hex 32`) |

Optional:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | Database host |
| `DB_PORT` | 5432 | Database port |
| `DB_NAME` | retail_price_intelligence | Database name |
| `DB_USER` | postgres | Database user |
| `LOG_LEVEL` | INFO | Logging level |

## Testing

```bash
cd server
python -m pytest tests/ -v
```

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
- **Database:** PostgreSQL, Redis
- **Infrastructure:** Docker, Alembic
- **Testing:** pytest

## License

MIT
