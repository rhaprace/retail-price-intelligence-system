from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from collections import defaultdict
import statistics

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from models import SessionLocal
from models.db_models import (
    Product, ProductSource, Price, Source,
    DiscountAnalysis, PriceComparison
)


class PriceAnalytics:
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
    
    def get_price_trend(
        self,
        product_source_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        prices = self.db.query(Price).filter(
            and_(
                Price.product_source_id == product_source_id,
                Price.scraped_at >= cutoff
            )
        ).order_by(Price.scraped_at).all()
        
        if not prices:
            return {'trend': 'unknown', 'data_points': 0}
        
        price_values = [float(p.price) for p in prices]
        
        current = price_values[-1]
        minimum = min(price_values)
        maximum = max(price_values)
        average = statistics.mean(price_values)
        
        n = len(price_values)
        if n >= 2:
            x_values = list(range(n))
            x_mean = statistics.mean(x_values)
            y_mean = average
            
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, price_values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            
            slope = numerator / denominator if denominator != 0 else 0
            
            normalized_slope = (slope / average * 100) if average != 0 else 0
            
            if normalized_slope > 1:
                trend = 'increasing'
            elif normalized_slope < -1:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
            slope = 0
            normalized_slope = 0
        
        if n >= 2:
            stddev = statistics.stdev(price_values)
            volatility = (stddev / average * 100) if average != 0 else 0
        else:
            volatility = 0
        
        first_price = price_values[0]
        price_change = current - first_price
        price_change_pct = (price_change / first_price * 100) if first_price != 0 else 0
        
        return {
            'trend': trend,
            'data_points': n,
            'current_price': current,
            'min_price': minimum,
            'max_price': maximum,
            'avg_price': round(average, 2),
            'price_change': round(price_change, 2),
            'price_change_pct': round(price_change_pct, 2),
            'slope': round(slope, 4),
            'normalized_slope': round(normalized_slope, 2),
            'volatility': round(volatility, 2),
            'first_date': prices[0].scraped_at.isoformat(),
            'last_date': prices[-1].scraped_at.isoformat()
        }
    
    def get_price_history_chart_data(
        self,
        product_source_id: int,
        days: int = 30,
        interval: str = 'daily'
    ) -> List[Dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        prices = self.db.query(Price).filter(
            and_(
                Price.product_source_id == product_source_id,
                Price.scraped_at >= cutoff
            )
        ).order_by(Price.scraped_at).all()
        
        if interval == 'daily':
            daily_prices = defaultdict(list)
            for p in prices:
                day = p.scraped_at.date().isoformat()
                daily_prices[day].append(float(p.price))
            
            return [
                {
                    'date': day,
                    'price': round(statistics.mean(day_prices), 2),
                    'min': min(day_prices),
                    'max': max(day_prices)
                }
                for day, day_prices in sorted(daily_prices.items())
            ]
        else:
            return [
                {
                    'timestamp': p.scraped_at.isoformat(),
                    'price': float(p.price),
                    'original_price': float(p.original_price) if p.original_price else None
                }
                for p in prices
            ]
    
    def compare_across_sources(
        self,
        product_id: str
    ) -> Dict[str, Any]:
        product_sources = self.db.query(ProductSource).filter(
            ProductSource.product_id == product_id,
            ProductSource.is_active == True
        ).all()
        
        if not product_sources:
            return {'sources': [], 'best_source': None}
        
        source_prices = []
        
        for ps in product_sources:
            latest_price = self.db.query(Price).filter(
                Price.product_source_id == ps.id
            ).order_by(desc(Price.scraped_at)).first()
            
            if latest_price:
                source = self.db.query(Source).filter(Source.id == ps.source_id).first()
                source_prices.append({
                    'source_id': ps.source_id,
                    'source_name': source.name if source else 'Unknown',
                    'product_source_id': ps.id,
                    'price': float(latest_price.price),
                    'original_price': float(latest_price.original_price) if latest_price.original_price else None,
                    'discount_pct': float(latest_price.discount_percentage) if latest_price.discount_percentage else None,
                    'in_stock': latest_price.is_in_stock,
                    'last_updated': latest_price.scraped_at.isoformat(),
                    'url': ps.source_product_url
                })
        
        if not source_prices:
            return {'sources': [], 'best_source': None}
        
        in_stock_prices = [s for s in source_prices if s['in_stock']]
        if in_stock_prices:
            best = min(in_stock_prices, key=lambda x: x['price'])
        else:
            best = min(source_prices, key=lambda x: x['price'])
        
        prices = [s['price'] for s in source_prices]
        
        return {
            'product_id': product_id,
            'sources': source_prices,
            'source_count': len(source_prices),
            'best_source': best['source_name'],
            'best_price': best['price'],
            'best_url': best['url'],
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': round(statistics.mean(prices), 2),
            'price_spread': round(max(prices) - min(prices), 2),
            'price_spread_pct': round((max(prices) - min(prices)) / min(prices) * 100, 2) if min(prices) > 0 else 0
        }
    
    def get_category_statistics(
        self,
        category: str,
        days: int = 30
    ) -> Dict[str, Any]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        products = self.db.query(Product).filter(
            Product.category == category
        ).all()
        
        if not products:
            return {'category': category, 'products': 0}
        
        all_prices = []
        product_stats = []
        
        for product in products:
            product_sources = self.db.query(ProductSource).filter(
                ProductSource.product_id == product.id,
                ProductSource.is_active == True
            ).all()
            
            product_prices = []
            for ps in product_sources:
                latest = self.db.query(Price).filter(
                    Price.product_source_id == ps.id,
                    Price.scraped_at >= cutoff
                ).order_by(desc(Price.scraped_at)).first()
                
                if latest:
                    product_prices.append(float(latest.price))
            
            if product_prices:
                avg_price = statistics.mean(product_prices)
                all_prices.extend(product_prices)
                product_stats.append({
                    'product_id': str(product.id),
                    'name': product.name,
                    'avg_price': round(avg_price, 2),
                    'source_count': len(product_prices)
                })
        
        if not all_prices:
            return {'category': category, 'products': len(products), 'data_points': 0}
        
        return {
            'category': category,
            'products': len(products),
            'products_with_prices': len(product_stats),
            'data_points': len(all_prices),
            'min_price': min(all_prices),
            'max_price': max(all_prices),
            'avg_price': round(statistics.mean(all_prices), 2),
            'median_price': round(statistics.median(all_prices), 2),
            'top_products': sorted(product_stats, key=lambda x: x['avg_price'])[:10]
        }
    
    def get_best_deals(
        self,
        limit: int = 20,
        min_discount: float = 10.0
    ) -> List[Dict[str, Any]]:
        analyses = self.db.query(DiscountAnalysis).filter(
            and_(
                DiscountAnalysis.actual_discount_percentage >= min_discount,
                DiscountAnalysis.is_fake_discount == False
            )
        ).order_by(desc(DiscountAnalysis.actual_discount_percentage)).limit(limit * 2).all()
        
        deals = []
        seen_products = set()
        
        for analysis in analyses:
            ps = self.db.query(ProductSource).filter(
                ProductSource.id == analysis.product_source_id
            ).first()
            
            if not ps or str(ps.product_id) in seen_products:
                continue
            
            product = self.db.query(Product).filter(Product.id == ps.product_id).first()
            source = self.db.query(Source).filter(Source.id == ps.source_id).first()
            
            if product and source:
                seen_products.add(str(ps.product_id))
                deals.append({
                    'product_id': str(product.id),
                    'product_name': product.name,
                    'source_name': source.name,
                    'current_price': float(analysis.current_price) if analysis.current_price else None,
                    'original_price': float(analysis.avg_price_90d) if analysis.avg_price_90d else None,
                    'discount_pct': float(analysis.actual_discount_percentage),
                    'price_trend': analysis.price_trend,
                    'url': ps.source_product_url,
                    'analysis_date': analysis.analysis_date.isoformat() if hasattr(analysis.analysis_date, 'isoformat') else str(analysis.analysis_date)
                })
                
                if len(deals) >= limit:
                    break
        
        return deals
    
    def get_price_volatility_report(
        self,
        days: int = 30,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        product_sources = self.db.query(ProductSource).filter(
            ProductSource.is_active == True
        ).all()
        
        volatility_data = []
        
        for ps in product_sources:
            prices = self.db.query(Price.price).filter(
                and_(
                    Price.product_source_id == ps.id,
                    Price.scraped_at >= cutoff
                )
            ).all()
            
            price_values = [float(p[0]) for p in prices]
            
            if len(price_values) >= 5:
                avg = statistics.mean(price_values)
                stddev = statistics.stdev(price_values)
                cv = (stddev / avg * 100) if avg > 0 else 0
                
                if cv > 5:
                    product = self.db.query(Product).filter(Product.id == ps.product_id).first()
                    source = self.db.query(Source).filter(Source.id == ps.source_id).first()
                    
                    if product and source:
                        volatility_data.append({
                            'product_id': str(product.id),
                            'product_name': product.name,
                            'source_name': source.name,
                            'volatility': round(cv, 2),
                            'avg_price': round(avg, 2),
                            'min_price': min(price_values),
                            'max_price': max(price_values),
                            'price_range': round(max(price_values) - min(price_values), 2),
                            'data_points': len(price_values)
                        })
        
        volatility_data.sort(key=lambda x: x['volatility'], reverse=True)
        
        return volatility_data[:limit]
    
    def close(self):

        if self.db:
            self.db.close()


class ReportGenerator:
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.analytics = PriceAnalytics(self.db)
    
    def generate_daily_summary(self) -> Dict[str, Any]:
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        
        total_products = self.db.query(func.count(Product.id)).scalar()
        total_sources = self.db.query(func.count(Source.id)).filter(Source.is_active == True).scalar()
        
        today_prices = self.db.query(func.count(Price.id)).filter(
            func.date(Price.scraped_at) == today
        ).scalar()
        
        fake_discounts = self.db.query(func.count(DiscountAnalysis.id)).filter(
            and_(
                func.date(DiscountAnalysis.analysis_date) == today,
                DiscountAnalysis.is_fake_discount == True
            )
        ).scalar()
        
        best_deals = self.analytics.get_best_deals(limit=5)
        
        volatile = self.analytics.get_price_volatility_report(days=7, limit=5)
        
        return {
            'report_date': today.isoformat(),
            'summary': {
                'total_products': total_products,
                'active_sources': total_sources,
                'prices_collected_today': today_prices,
                'fake_discounts_detected': fake_discounts
            },
            'top_deals': best_deals,
            'most_volatile': volatile
        }
    
    def generate_source_performance_report(self) -> List[Dict[str, Any]]:
        sources = self.db.query(Source).filter(Source.is_active == True).all()
        
        report = []
        for source in sources:
            product_count = self.db.query(func.count(ProductSource.id)).filter(
                ProductSource.source_id == source.id,
                ProductSource.is_active == True
            ).scalar()
            
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_prices = self.db.query(func.count(Price.id)).join(ProductSource).filter(
                ProductSource.source_id == source.id,
                Price.scraped_at >= week_ago
            ).scalar()
            
            report.append({
                'source_id': source.id,
                'source_name': source.name,
                'base_url': source.base_url,
                'product_count': product_count,
                'prices_last_7_days': recent_prices,
                'last_scraped': source.last_scraped_at.isoformat() if source.last_scraped_at else None,
                'rate_limit': source.rate_limit_per_minute
            })
        
        return sorted(report, key=lambda x: x['product_count'], reverse=True)
    
    def close(self):
        self.analytics.close()
