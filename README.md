# Retail Price Intelligence System

A comprehensive system for scraping, tracking, and analyzing product prices across multiple e-commerce websites. Built with Python, PostgreSQL.

## Overview

This system provides end-to-end price intelligence capabilities:
- **Data Collection**: Multi-source web scraping with rate limiting and error handling
- **Data Storage**: PostgreSQL data warehouse optimized for time-series analysis
- **Analytics**: Automated price comparison, fake discount detection, and trend analysis
- **API Layer**: RESTful API for accessing all features and data

## Architecture

### System Flow

```
┌─────────────┐
│   Scrapers  │ → Collect product prices from e-commerce sites
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │ → Store prices, products, sources (PostgreSQL)
└──────┬──────┘
       │
       ├──► ┌──────────┐
       │    │ Pipeline │ → Analytics & intelligence tasks
       │    └────┬─────┘
       │         │
       └─────────┴──► ┌─────┐
                      │ API │ → Expose data & features (FastAPI)
                      └─────┘
```

### Design Principles

- **DRY (Don't Repeat Yourself)**: Shared utilities, base classes, and common patterns
- **SOLID**: Single responsibility per module, clear separation of concerns
- **KISS (Keep It Simple)**: Straightforward code, minimal abstractions
- **Modularity**: Each component is independent and reusable

## Project Structure

```
retail-price-intelligence-system/
├── api/                      # REST API layer
│   ├── main.py              # FastAPI application entry point
│   ├── dependencies.py      # Shared database dependencies
│   └── routes/               # API endpoint modules
│       ├── products.py       # Product CRUD operations
│       ├── prices.py         # Price queries and history
│       ├── sources.py        # Source management
│       ├── comparisons.py    # Price comparison endpoints
│       ├── alerts.py         # Price alert management
│       └── analytics.py      # Analytics and discount analysis
│
├── scrapers/                 # Web scraping infrastructure
│   ├── base.py              # Base scraper class (abstract)
│   └── setup_source.py      # Helper to add sources to database
│
├── pipeline/                 # ETL and analytics pipeline
│   ├── orchestrator.py      # Pipeline task coordinator
│   ├── tasks.py             # Analytics task implementations
│   └── runner.py            # Command-line pipeline runner
│
├── models/                   # Data models and schemas
│   ├── base.py              # SQLAlchemy base configuration
│   ├── db_models.py         # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic validation schemas
│   └── utils.py             # Database utility functions
│
├── database/                 # Database schema and utilities
│   ├── schema.sql           # Complete database schema
│   ├── connection.py        # Database connection pooling
│   └── README.md            # Schema documentation
│
├── config/                   # Configuration management
│   └── settings.py          # Application settings from env vars
│
├── utils/                    # Shared utilities
│   ├── http_client.py       # HTTP client with retry logic
│   └── rate_limiter.py     # Rate limiting implementation
│
├── analytics/                # Analytics modules (future)
│
└── tests/                    # Test files
```

## Components

### 1. Database Layer (`database/`, `models/`)

**Purpose**: Data persistence and modeling

**Key Files**:
- `database/schema.sql`: Complete PostgreSQL schema with tables, indexes, triggers, and views
- `models/db_models.py`: SQLAlchemy ORM models (Source, Product, Price, etc.)
- `models/schemas.py`: Pydantic schemas for API validation
- `models/utils.py`: Helper functions for common database operations

**Design**:
- Normalized schema: Products separate from source-specific data
- Time-series optimized: Prices table designed for historical analysis
- Auto-calculations: Database triggers compute discount percentages
- Views: Pre-built queries for common operations (latest_prices, price_comparison_view)

### 2. Scraping Layer (`scrapers/`)

**Purpose**: Web scraping infrastructure

**Key Files**:
- `scrapers/base.py`: Abstract base class for all scrapers
  - Handles rate limiting, database integration, error logging
  - Provides price extraction helpers
  - Manages HTTP client and session lifecycle
- `scrapers/setup_source.py`: Utility to add e-commerce sources

**Design**:
- Base class pattern: Common functionality in base, site-specific logic in subclasses
- Rate limiting: Per-source rate limits from database configuration
- Error handling: Comprehensive logging and retry logic
- Database integration: Automatic product matching and price storage

### 3. Pipeline Layer (`pipeline/`)

**Purpose**: Data processing and analytics orchestration

**Key Files**:
- `pipeline/orchestrator.py`: Coordinates task execution
- `pipeline/tasks.py`: Task implementations
  - `DiscountAnalysisTask`: Detects fake discounts, calculates metrics
  - `PriceComparisonTask`: Compares prices across sources
  - `PriceAlertTask`: Checks and triggers price alerts
- `pipeline/runner.py`: Command-line interface

**Design**:
- Task-based: Each analytics operation is a separate task
- Orchestration: Tasks can run individually or as a pipeline
- Error isolation: Task failures don't stop the pipeline
- Results tracking: Detailed execution results and metrics

### 4. API Layer (`api/`)

**Purpose**: REST API for accessing system features

**Key Files**:
- `api/main.py`: FastAPI application setup and route registration
- `api/dependencies.py`: Shared dependencies (database sessions, error handling)
- `api/routes/`: Resource-specific endpoints

**Design**:
- RESTful: Standard HTTP methods and status codes
- Type-safe: Pydantic schemas for request/response validation
- Error handling: Consistent error responses with detailed messages
- Auto-documentation: Swagger UI and ReDoc generated automatically

### 5. Utilities (`utils/`, `config/`)

**Purpose**: Shared infrastructure components

**Key Files**:
- `utils/http_client.py`: HTTP client with retry and timeout handling
- `utils/rate_limiter.py`: Token bucket rate limiting algorithm
- `config/settings.py`: Centralized configuration from environment variables

**Design**:
- Reusable: Used across scrapers and API
- Configurable: Settings via environment variables
- Robust: Built-in retry logic and error handling

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Step 1: Install Dependencies

**Option A: Using pip (recommended for development)**
```bash
pip install -r requirements.txt
```

**Option B: Using setup.py (for package installation)**
```bash
pip install -e .
```

This installs the package in editable mode, making it available as a Python package.

### Step 2: Setup Database

**Automated Setup**:
```bash
python setup_database.py
```

**Manual Setup**:
```bash
# Create database
createdb -U postgres retail_price_intelligence

# Run schema
psql -U postgres -d retail_price_intelligence -f database/schema.sql
```

### Step 3: Configuration

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=retail_price_intelligence
DB_USER=postgres
DB_PASSWORD=your_password
```

See `env.example` for all available configuration options.

### Step 4: Verify Setup

```bash
# Test database connection
python check_db_connection.py

# Should show: ✅ Connection successful!
```

## Usage

### Starting the API Server

```bash
python run_api.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Adding E-commerce Sources

```python
from scrapers.setup_source import add_source

add_source(
    name="Amazon US",
    base_url="https://www.amazon.com",
    country_code="US",
    currency_code="USD",
    rate_limit=60  # requests per minute
)
```

### Creating a Custom Scraper

```python
from scrapers.base import BaseScraper
from bs4 import BeautifulSoup
from decimal import Decimal

class MySiteScraper(BaseScraper):
    def scrape_product(self, product_url: str):
        """Implement site-specific scraping logic."""
        response = self.http_client.get(product_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product data
        name = soup.select_one('h1.product-title').get_text()
        price_text = soup.select_one('.price').get_text()
        price = self._extract_price(price_text)
        
        return {
            'name': name,
            'price': price,
            'source_product_id': 'extract-from-url',
            'source_product_url': product_url,
            'source_product_name': name,
            'is_in_stock': True
        }

# Usage
scraper = MySiteScraper('Amazon US')
results = scraper.scrape(['url1', 'url2', 'url3'])
scraper.close()
```

### Running Analytics Pipeline

```bash
# Run full analytics pipeline
python -m pipeline.runner analytics

# Run individual tasks
python -m pipeline.runner discounts      # Fake discount detection
python -m pipeline.runner comparison     # Price comparisons
python -m pipeline.runner alerts         # Check price alerts
```

### Using the API

**Get Products**:
```bash
curl http://localhost:8000/api/products/?category=Electronics&limit=10
```

**Get Price History**:
```bash
curl http://localhost:8000/api/prices/product-source/1?days=30
```

**Get Fake Discounts**:
```bash
curl http://localhost:8000/api/analytics/discounts/fake?limit=50
```

**Create Price Alert**:
```bash
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "123e4567-e89b-12d3-a456-426614174000",
    "target_price": 99.99,
    "is_active": true
  }'
```

## API Endpoints

### Products
- `GET /api/products/` - List products (filters: category, brand, search)
- `GET /api/products/{id}` - Get product details
- `POST /api/products/` - Create product
- `GET /api/products/{id}/sources` - Get sources for product
- `GET /api/products/{id}/prices` - Get price history

### Prices
- `GET /api/prices/latest` - Get latest prices
- `GET /api/prices/product-source/{id}` - Get price history
- `GET /api/prices/product-source/{id}/metrics` - Get price metrics

### Sources
- `GET /api/sources/` - List all sources
- `GET /api/sources/{id}` - Get source details
- `POST /api/sources/` - Create source

### Comparisons
- `GET /api/comparisons/` - Get price comparisons
- `GET /api/comparisons/product/{id}` - Get comparison for product

### Alerts
- `GET /api/alerts/` - List alerts
- `POST /api/alerts/` - Create alert
- `PATCH /api/alerts/{id}/activate` - Activate alert
- `PATCH /api/alerts/{id}/deactivate` - Deactivate alert

### Analytics
- `GET /api/analytics/discounts` - Get discount analysis
- `GET /api/analytics/discounts/fake` - Get fake discounts
- `GET /api/analytics/discounts/product-source/{id}` - Get analysis for product-source

## Testing

```bash
# Test database connection
python check_db_connection.py

# Test API endpoints
python test_api.py

# Interactive API testing
# Visit: http://localhost:8000/docs
```

## Database Schema

The system uses a normalized PostgreSQL schema with 8 core tables:

1. **sources** - E-commerce websites metadata
2. **products** - Universal product catalog
3. **product_sources** - Links products to sources
4. **prices** - Time-series price data
5. **price_alerts** - Price drop notifications
6. **discount_analysis** - Fake discount detection results
7. **price_comparisons** - Cross-source price comparisons
8. **scraping_logs** - Scraping activity tracking

See [database/README.md](database/README.md) for detailed schema documentation.

## Development

### Key Design Patterns

- **Base Class Pattern**: `BaseScraper` for common scraping functionality
- **Task Pattern**: Pipeline tasks for analytics operations
- **Dependency Injection**: FastAPI dependencies for database sessions
- **Repository Pattern**: Utility functions abstract database operations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## CI/CD

The project includes a minimal CI/CD pipeline using GitHub Actions:

- **Lint Check**: Runs flake8 to check code quality and style
- **Deployment Check**: Verifies module imports and configuration on main branch

The pipeline runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

See `.github/workflows/ci-cd.yml` for configuration details.
