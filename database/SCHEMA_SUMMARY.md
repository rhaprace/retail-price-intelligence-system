# Database Schema Summary

## Quick Reference

### Table Count: 8 Core Tables

1. **sources** - E-commerce websites metadata
2. **products** - Core product catalog
3. **product_sources** - Links products to sources
4. **prices** - Time-series price data (main analytics table)
5. **price_alerts** - Price drop notifications
6. **discount_analysis** - Fake discount detection
7. **price_comparisons** - Cross-source price comparisons
8. **scraping_logs** - Operational scraping tracking

## Key Design Decisions

### 1. Normalized Product Model
- **products**: Universal product catalog (one product, multiple sources)
- **product_sources**: Source-specific mappings (URLs, IDs, names)
- **Benefits**: 
  - Easy cross-source price comparison
  - Product matching and deduplication
  - Single source of truth for product data

### 2. Time-Series Optimized Prices Table
- Primary table for all price data
- Indexed on `(product_source_id, scraped_at DESC)`
- Supports TimescaleDB hypertable conversion
- Stores both current and original prices for discount calculation

### 3. Analytics Tables
- **discount_analysis**: Pre-computed 30/60/90 day metrics
- **price_comparisons**: Daily snapshots of best prices
- **Benefits**: Fast queries without real-time aggregation

### 4. UUID vs Serial IDs
- **products**: UUID (distributed system friendly)
- **prices**: BIGSERIAL (high volume, sequential)
- **Other tables**: SERIAL (standard auto-increment)

## Data Flow

```
Scraping → product_sources → prices → discount_analysis
                                    → price_comparisons
                                    → price_alerts (if triggered)
```

## Index Strategy

### High-Performance Indexes
- **Time-series queries**: `idx_prices_product_source_scraped`
- **Latest prices**: `idx_prices_product_source_scraped` (DESC order)
- **Product search**: `idx_products_normalized_name` (GIN trigram)
- **Active products**: Partial indexes on `is_active = TRUE`

### Composite Indexes
- `(product_source_id, scraped_at DESC, price)` - Common lookup pattern
- Optimized for: "Get price history for product X"

## Features Enabled

**Price Comparison**: Cross-source aggregation via `price_comparison_view`
**Price Drop Detection**: Alert triggers on price changes
**Fake Discount Detection**: Historical min vs claimed discount
**Historical Trends**: Time-series data with 30/60/90 day windows
**Fuzzy Product Matching**: Trigram indexes on normalized names
**Auto-calculations**: Discount percentages computed automatically

## Performance Considerations

### TimescaleDB (Recommended)
- Convert `prices` table to hypertable
- Automatic chunking by day
- Built-in compression and retention policies
- Optimized for time-series queries

### Without TimescaleDB
- Consider table partitioning on `scraped_at` date
- Implement manual data retention policies
- Monitor index bloat on high-write tables

## Scalability Notes

- **Prices table**: Designed for millions of rows
- **Partitioning**: Ready for TimescaleDB or manual partitioning
- **Indexes**: Balanced for read/write performance
- **JSONB storage**: `raw_data` field for flexible metadata

## Security Considerations

- Use connection pooling (implemented in `connection.py`)
- Parameterized queries (prevent SQL injection)
- Environment variables for credentials
- Row-level security can be added if needed

## Next Steps

1. Schema designed
2. ⏭Create data models (SQLAlchemy/Pydantic)
3. ⏭Implement scraper data insertion
4. ⏭Build analytics queries
5. ⏭Set up TimescaleDB (optional)

