CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    base_url VARCHAR(500) NOT NULL,
    country_code CHAR(2),
    currency_code CHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit_per_minute INTEGER DEFAULT 60,
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    brand VARCHAR(100),
    sku VARCHAR(100),
    upc VARCHAR(50),
    ean VARCHAR(50),
    image_url VARCHAR(1000),
    normalized_name VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_sources (
    id SERIAL PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    source_product_id VARCHAR(200) NOT NULL,
    source_product_url VARCHAR(1000) NOT NULL,
    source_product_name VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    last_seen_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, source_product_id)
);

CREATE TABLE prices (
    id BIGSERIAL PRIMARY KEY,
    product_source_id INTEGER NOT NULL REFERENCES product_sources(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    currency_code CHAR(3) DEFAULT 'USD',
    original_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    is_in_stock BOOLEAN DEFAULT TRUE,
    stock_quantity INTEGER,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    scraped_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE price_alerts (
    id SERIAL PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_email VARCHAR(255),
    target_price DECIMAL(10, 2),
    price_drop_percentage DECIMAL(5, 2),
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE discount_analysis (
    id SERIAL PRIMARY KEY,
    product_source_id INTEGER NOT NULL REFERENCES product_sources(id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL,
    min_price_30d DECIMAL(10, 2),
    max_price_30d DECIMAL(10, 2),
    avg_price_30d DECIMAL(10, 2),
    min_price_60d DECIMAL(10, 2),
    max_price_60d DECIMAL(10, 2),
    avg_price_60d DECIMAL(10, 2),
    min_price_90d DECIMAL(10, 2),
    max_price_90d DECIMAL(10, 2),
    avg_price_90d DECIMAL(10, 2),
    current_price DECIMAL(10, 2),
    claimed_discount_percentage DECIMAL(5, 2),
    actual_discount_percentage DECIMAL(5, 2),
    is_fake_discount BOOLEAN DEFAULT FALSE,
    fake_discount_reason TEXT,
    price_trend VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_source_id, analysis_date)
);

CREATE TABLE price_comparisons (
    id SERIAL PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    comparison_date DATE NOT NULL,
    best_price DECIMAL(10, 2),
    best_price_source_id INTEGER REFERENCES sources(id),
    best_price_product_source_id INTEGER REFERENCES product_sources(id),
    min_price DECIMAL(10, 2),
    max_price DECIMAL(10, 2),
    price_variance DECIMAL(10, 2),
    source_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, comparison_date)
);

CREATE TABLE scraping_logs (
    id BIGSERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id) ON DELETE SET NULL,
    product_source_id INTEGER REFERENCES product_sources(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    response_time_ms INTEGER,
    http_status_code INTEGER,
    scraped_count INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_normalized_name ON products USING gin(normalized_name gin_trgm_ops);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_sku ON products(sku) WHERE sku IS NOT NULL;
CREATE INDEX idx_products_upc ON products(upc) WHERE upc IS NOT NULL;
CREATE INDEX idx_products_ean ON products(ean) WHERE ean IS NOT NULL;

CREATE INDEX idx_product_sources_product_id ON product_sources(product_id);
CREATE INDEX idx_product_sources_source_id ON product_sources(source_id);
CREATE INDEX idx_product_sources_active ON product_sources(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_product_sources_source_product_id ON product_sources(source_product_id);

CREATE INDEX idx_prices_product_source_id ON prices(product_source_id);
CREATE INDEX idx_prices_scraped_at ON prices(scraped_at DESC);
CREATE INDEX idx_prices_product_source_scraped ON prices(product_source_id, scraped_at DESC);
CREATE INDEX idx_prices_in_stock ON prices(is_in_stock) WHERE is_in_stock = TRUE;
CREATE INDEX idx_prices_lookup ON prices(product_source_id, scraped_at DESC, price);

CREATE INDEX idx_price_alerts_product_id ON price_alerts(product_id);
CREATE INDEX idx_price_alerts_active ON price_alerts(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_discount_analysis_product_source ON discount_analysis(product_source_id);
CREATE INDEX idx_discount_analysis_date ON discount_analysis(analysis_date DESC);
CREATE INDEX idx_discount_analysis_fake ON discount_analysis(is_fake_discount) WHERE is_fake_discount = TRUE;

CREATE INDEX idx_price_comparisons_product_id ON price_comparisons(product_id);
CREATE INDEX idx_price_comparisons_date ON price_comparisons(comparison_date DESC);

CREATE INDEX idx_scraping_logs_source_id ON scraping_logs(source_id);
CREATE INDEX idx_scraping_logs_status ON scraping_logs(status);
CREATE INDEX idx_scraping_logs_started_at ON scraping_logs(started_at DESC);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_sources_updated_at BEFORE UPDATE ON product_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_price_alerts_updated_at BEFORE UPDATE ON price_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION calculate_discount_percentage(
    current_price DECIMAL,
    original_price DECIMAL
)
RETURNS DECIMAL AS $$
BEGIN
    IF original_price IS NULL OR original_price <= 0 THEN
        RETURN NULL;
    END IF;
    RETURN ROUND(((original_price - current_price) / original_price) * 100, 2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION auto_calculate_discount()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.original_price IS NOT NULL AND NEW.original_price > NEW.price THEN
        NEW.discount_percentage = calculate_discount_percentage(NEW.price, NEW.original_price);
    ELSE
        NEW.discount_percentage = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_discount_trigger BEFORE INSERT OR UPDATE ON prices
    FOR EACH ROW EXECUTE FUNCTION auto_calculate_discount();

CREATE OR REPLACE VIEW latest_prices AS
SELECT DISTINCT ON (ps.id)
    p.id AS product_id,
    p.name AS product_name,
    s.name AS source_name,
    s.id AS source_id,
    ps.id AS product_source_id,
    pr.price,
    pr.currency_code,
    pr.original_price,
    pr.discount_percentage,
    pr.is_in_stock,
    pr.scraped_at,
    pr.created_at
FROM products p
JOIN product_sources ps ON p.id = ps.product_id
JOIN sources s ON ps.source_id = s.id
JOIN prices pr ON ps.id = pr.product_source_id
WHERE ps.is_active = TRUE
ORDER BY ps.id, pr.scraped_at DESC;

CREATE OR REPLACE VIEW price_comparison_view AS
SELECT 
    p.id AS product_id,
    p.name AS product_name,
    COUNT(DISTINCT ps.id) AS source_count,
    MIN(lp.price) AS min_price,
    MAX(lp.price) AS max_price,
    AVG(lp.price) AS avg_price,
    STDDEV(lp.price) AS price_stddev,
    MAX(lp.scraped_at) AS last_updated
FROM products p
JOIN product_sources ps ON p.id = ps.product_id
JOIN latest_prices lp ON ps.id = lp.product_source_id
WHERE ps.is_active = TRUE
GROUP BY p.id, p.name;
