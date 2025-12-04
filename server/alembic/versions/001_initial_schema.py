from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('base_url', sa.String(500), nullable=False),
        sa.Column('country_code', sa.String(2)),
        sa.Column('currency_code', sa.String(3), server_default='USD'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('rate_limit_per_minute', sa.Integer(), server_default='60'),
        sa.Column('last_scraped_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('category', sa.String(100)),
        sa.Column('brand', sa.String(100)),
        sa.Column('sku', sa.String(100)),
        sa.Column('upc', sa.String(50)),
        sa.Column('ean', sa.String(50)),
        sa.Column('image_url', sa.String(1000)),
        sa.Column('normalized_name', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    op.create_table(
        'product_sources',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_id', sa.Integer(), sa.ForeignKey('sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_product_id', sa.String(200), nullable=False),
        sa.Column('source_product_url', sa.String(1000), nullable=False),
        sa.Column('source_product_name', sa.String(500)),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_seen_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('source_id', 'source_product_id', name='uq_source_product'),
    )
    
    op.create_table(
        'prices',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('product_source_id', sa.Integer(), sa.ForeignKey('product_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency_code', sa.String(3), server_default='USD'),
        sa.Column('original_price', sa.Numeric(10, 2)),
        sa.Column('discount_percentage', sa.Numeric(5, 2)),
        sa.Column('is_in_stock', sa.Boolean(), server_default='true'),
        sa.Column('stock_quantity', sa.Integer()),
        sa.Column('shipping_cost', sa.Numeric(10, 2), server_default='0'),
        sa.Column('scraped_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('raw_data', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('price > 0', name='check_price_positive'),
    )
    
    op.create_table(
        'price_alerts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_email', sa.String(255)),
        sa.Column('target_price', sa.Numeric(10, 2)),
        sa.Column('price_drop_percentage', sa.Numeric(5, 2)),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_triggered_at', sa.DateTime(timezone=True)),
        sa.Column('trigger_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    op.create_table(
        'discount_analysis',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_source_id', sa.Integer(), sa.ForeignKey('product_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analysis_date', sa.Date(), nullable=False),
        sa.Column('min_price_30d', sa.Numeric(10, 2)),
        sa.Column('max_price_30d', sa.Numeric(10, 2)),
        sa.Column('avg_price_30d', sa.Numeric(10, 2)),
        sa.Column('min_price_60d', sa.Numeric(10, 2)),
        sa.Column('max_price_60d', sa.Numeric(10, 2)),
        sa.Column('avg_price_60d', sa.Numeric(10, 2)),
        sa.Column('min_price_90d', sa.Numeric(10, 2)),
        sa.Column('max_price_90d', sa.Numeric(10, 2)),
        sa.Column('avg_price_90d', sa.Numeric(10, 2)),
        sa.Column('current_price', sa.Numeric(10, 2)),
        sa.Column('claimed_discount_percentage', sa.Numeric(5, 2)),
        sa.Column('actual_discount_percentage', sa.Numeric(5, 2)),
        sa.Column('is_fake_discount', sa.Boolean(), server_default='false'),
        sa.Column('fake_discount_reason', sa.Text()),
        sa.Column('price_trend', sa.String(20)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('product_source_id', 'analysis_date', name='uq_discount_analysis'),
    )
    
    op.create_table(
        'price_comparisons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('comparison_date', sa.Date(), nullable=False),
        sa.Column('best_price', sa.Numeric(10, 2)),
        sa.Column('best_price_source_id', sa.Integer(), sa.ForeignKey('sources.id')),
        sa.Column('best_price_product_source_id', sa.Integer(), sa.ForeignKey('product_sources.id')),
        sa.Column('min_price', sa.Numeric(10, 2)),
        sa.Column('max_price', sa.Numeric(10, 2)),
        sa.Column('price_variance', sa.Numeric(10, 2)),
        sa.Column('source_count', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('product_id', 'comparison_date', name='uq_price_comparison'),
    )
    
    op.create_table(
        'scraping_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('source_id', sa.Integer(), sa.ForeignKey('sources.id', ondelete='SET NULL')),
        sa.Column('product_source_id', sa.Integer(), sa.ForeignKey('product_sources.id', ondelete='SET NULL')),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text()),
        sa.Column('response_time_ms', sa.Integer()),
        sa.Column('http_status_code', sa.Integer()),
        sa.Column('scraped_count', sa.Integer(), server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    op.create_index('idx_products_name', 'products', ['name'])
    op.create_index('idx_products_category', 'products', ['category'])
    op.create_index('idx_products_sku', 'products', ['sku'], postgresql_where=sa.text('sku IS NOT NULL'))
    
    op.create_index('idx_product_sources_product_id', 'product_sources', ['product_id'])
    op.create_index('idx_product_sources_source_id', 'product_sources', ['source_id'])
    
    op.create_index('idx_prices_product_source_id', 'prices', ['product_source_id'])
    op.create_index('idx_prices_scraped_at', 'prices', [sa.text('scraped_at DESC')])
    op.create_index('idx_prices_lookup', 'prices', ['product_source_id', sa.text('scraped_at DESC'), 'price'])
    
    op.create_index('idx_price_alerts_product_id', 'price_alerts', ['product_id'])
    
    op.create_index('idx_discount_analysis_product_source', 'discount_analysis', ['product_source_id'])
    op.create_index('idx_discount_analysis_date', 'discount_analysis', [sa.text('analysis_date DESC')])
    
    op.create_index('idx_price_comparisons_product_id', 'price_comparisons', ['product_id'])
    
    op.create_index('idx_scraping_logs_source_id', 'scraping_logs', ['source_id'])
    op.create_index('idx_scraping_logs_status', 'scraping_logs', ['status'])
    
    op.create_index('idx_users_email', 'users', ['email'])


def downgrade() -> None:
    op.drop_table('scraping_logs')
    op.drop_table('price_comparisons')
    op.drop_table('discount_analysis')
    op.drop_table('price_alerts')
    op.drop_table('prices')
    op.drop_table('product_sources')
    op.drop_table('products')
    op.drop_table('sources')
    op.drop_table('users')
