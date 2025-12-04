# Database Schema Documentation

## Overview
This database schema is designed for a Retail Price Intelligence System that tracks product prices across multiple e-commerce websites, analyzes price trends, and detects fake discounts.

## Database Requirements
- PostgreSQL 12+ (recommended: PostgreSQL 14+)
- Optional: TimescaleDB extension for time-series optimization

## Schema Structure

### Core Tables

#### `sources`
Stores metadata about e-commerce websites being scraped.
- Tracks scraping rate limits, last scraped time
- Stores base URLs and currency information

#### `products`
Core product catalog with normalized product information.
- Supports multiple identifiers (SKU, UPC, EAN) for product matching
- Includes normalized_name for fuzzy matching across sources

#### `product_sources`
Links products to specific sources with source-specific identifiers.
- Maps products to their URLs and IDs on each e-commerce site
- Tracks if product is still active on source

#### `prices`
Time-series table storing all price data.
- Main table for analytics and trend analysis
- Stores current price, original price, discount percentage
- Includes stock status and shipping costs
- Can be converted to TimescaleDB hypertable for optimization

### Analytics Tables

#### `price_alerts`
Tracks price drop alerts and notifications.
- Supports target price and percentage-based alerts
- Tracks trigger count and last triggered time

#### `discount_analysis`
Analyzes discount claims vs historical reality.
- Stores 30/60/90 day price metrics
- Flags fake discounts
- Tracks price trends

#### `price_comparisons`
Stores comparison results across multiple sources.
- Best price identification
- Price variance calculations
- Source count tracking

### Operational Tables

#### `scraping_logs`
Tracks scraping activities, errors, and performance.
- Monitors scraping success/failure rates
- Tracks response times and HTTP status codes

## Key Features

### Indexes
- Optimized indexes for time-series queries on prices
- Full-text search support on product names
- Composite indexes for common query patterns

### Functions & Triggers
- Auto-calculation of discount percentages
- Automatic `updated_at` timestamp management
- Discount calculation helper function

### Views
- `latest_prices`: Latest price for each product-source combination
- `price_comparison_view`: Aggregated price comparison across sources

## Installation

1. Create PostgreSQL database:
```bash
createdb retail_price_intelligence
```

2. Install TimescaleDB (optional but recommended):
```bash
# Follow TimescaleDB installation guide for your OS
# https://docs.timescale.com/install/latest/
```

3. Run schema:
```bash
psql -d retail_price_intelligence -f schema.sql
```

## TimescaleDB Optimization

If using TimescaleDB, uncomment the hypertable creation line in `schema.sql`:
```sql
SELECT create_hypertable('prices', 'scraped_at', chunk_time_interval => INTERVAL '1 day');
```

This will:
- Optimize time-series queries on the prices table
- Enable automatic data retention policies
- Improve query performance for historical analysis

## Data Model Relationships

```
sources (1) ──< (many) product_sources (many) ──> (1) products
                                                          │
                                                          │
                                                          ▼
                                                    prices (many)
                                                          │
                                                          │
                                                          ▼
                                            discount_analysis (many)
                                                          │
                                                          │
                                                          ▼
                                            price_comparisons (many)
```

## Common Queries

### Get latest price for a product
```sql
SELECT * FROM latest_prices WHERE product_id = '...';
```

### Compare prices across sources
```sql
SELECT * FROM price_comparison_view WHERE product_id = '...';
```

### Find fake discounts
```sql
SELECT * FROM discount_analysis 
WHERE is_fake_discount = TRUE 
ORDER BY analysis_date DESC;
```

### Get price history for a product
```sql
SELECT price, scraped_at 
FROM prices 
WHERE product_source_id = ...
ORDER BY scraped_at DESC;
```

## Maintenance

### Regular Maintenance Tasks
1. **Data Retention**: Implement retention policies for old price data (if using TimescaleDB)
2. **Index Maintenance**: Run `REINDEX` periodically on frequently updated tables
3. **Vacuum**: Regular `VACUUM ANALYZE` on tables with high write activity
4. **Archiving**: Consider archiving old scraping logs to separate tables

### Performance Tuning
- Monitor query performance using `EXPLAIN ANALYZE`
- Adjust chunk_time_interval for TimescaleDB based on data volume
- Consider partitioning large tables if not using TimescaleDB

