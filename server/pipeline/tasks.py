"""
Pipeline tasks for data processing and analytics.
"""
from typing import List, Dict, Any
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from models import SessionLocal
from models.db_models import (
    ProductSource, Price, Product,
    DiscountAnalysis, PriceComparison, PriceAlert
)
from models.utils import calculate_price_metrics


class Task:
    """Base task class."""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def execute(self) -> Dict[str, Any]:
        """Execute the task."""
        raise NotImplementedError
    
    def close(self):
        """Clean up resources."""
        if self.db:
            self.db.close()


class DiscountAnalysisTask(Task):
    """Analyze discounts and detect fake discounts."""
    
    def execute(self) -> Dict[str, Any]:
        """Run discount analysis for all active product sources."""
        results = {
            'analyzed': 0,
            'fake_discounts_found': 0,
            'errors': []
        }
        
        today = date.today()
        product_sources = self.db.query(ProductSource).filter(
            ProductSource.is_active == True
        ).all()
        
        for ps in product_sources:
            try:
                latest_price = self.db.query(Price).filter(
                    Price.product_source_id == ps.id
                ).order_by(Price.scraped_at.desc()).first()
                
                if not latest_price:
                    continue
                
                metrics_30d = calculate_price_metrics(self.db, ps.id, days=30)
                metrics_60d = calculate_price_metrics(self.db, ps.id, days=60)
                metrics_90d = calculate_price_metrics(self.db, ps.id, days=90)
                
                is_fake = False
                fake_reason = None
                actual_discount = None
                
                if latest_price.original_price and metrics_90d['min_price']:
                    claimed_discount = latest_price.discount_percentage or 0
                    historical_min = metrics_90d['min_price']
                    
                    if latest_price.price > historical_min:
                        is_fake = True
                        fake_reason = f"Current price (${latest_price.price}) higher than 90-day minimum (${historical_min})"
                    
                    if historical_min > 0:
                        actual_discount = float((latest_price.price - historical_min) / historical_min * 100)
                
                trend = self._determine_trend(metrics_30d, metrics_60d, metrics_90d)
                
                analysis = self.db.query(DiscountAnalysis).filter(
                    and_(
                        DiscountAnalysis.product_source_id == ps.id,
                        DiscountAnalysis.analysis_date == today
                    )
                ).first()
                
                if not analysis:
                    analysis = DiscountAnalysis(
                        product_source_id=ps.id,
                        analysis_date=today
                    )
                    self.db.add(analysis)
                
                analysis.min_price_30d = metrics_30d['min_price']
                analysis.max_price_30d = metrics_30d['max_price']
                analysis.avg_price_30d = metrics_30d['avg_price']
                analysis.min_price_60d = metrics_60d['min_price']
                analysis.max_price_60d = metrics_60d['max_price']
                analysis.avg_price_60d = metrics_60d['avg_price']
                analysis.min_price_90d = metrics_90d['min_price']
                analysis.max_price_90d = metrics_90d['max_price']
                analysis.avg_price_90d = metrics_90d['avg_price']
                analysis.current_price = latest_price.price
                analysis.claimed_discount_percentage = latest_price.discount_percentage
                analysis.actual_discount_percentage = Decimal(str(actual_discount)) if actual_discount else None
                analysis.is_fake_discount = is_fake
                analysis.fake_discount_reason = fake_reason
                analysis.price_trend = trend
                
                self.db.commit()
                results['analyzed'] += 1
                
                if is_fake:
                    results['fake_discounts_found'] += 1
                    
            except Exception as e:
                results['errors'].append(f"Error analyzing {ps.id}: {str(e)}")
        
        return results
    
    def _determine_trend(self, metrics_30d, metrics_60d, metrics_90d) -> str:
        """Determine price trend based on metrics."""
        if not all([metrics_30d['avg_price'], metrics_60d['avg_price'], metrics_90d['avg_price']]):
            return 'unknown'
        
        avg_30 = float(metrics_30d['avg_price'])
        avg_60 = float(metrics_60d['avg_price'])
        avg_90 = float(metrics_90d['avg_price'])
        
        if avg_30 > avg_60 * 1.05:
            return 'increasing'
        elif avg_30 < avg_60 * 0.95:
            return 'decreasing'
        elif abs(avg_30 - avg_60) / avg_60 < 0.05:
            return 'stable'
        else:
            return 'volatile'


class PriceComparisonTask(Task):
    """Compare prices across sources for each product."""
    
    def execute(self) -> Dict[str, Any]:
        """Generate price comparisons for all products."""
        results = {
            'compared': 0,
            'errors': []
        }
        
        today = date.today()
        
        products = self.db.query(Product).join(ProductSource).filter(
            ProductSource.is_active == True
        ).group_by(Product.id).having(func.count(ProductSource.id) > 1).all()
        
        for product in products:
            try:
                product_sources = self.db.query(ProductSource).filter(
                    ProductSource.product_id == product.id,
                    ProductSource.is_active == True
                ).all()
                
                latest_prices = []
                for ps in product_sources:
                    latest_price = self.db.query(Price).filter(
                        Price.product_source_id == ps.id
                    ).order_by(Price.scraped_at.desc()).first()
                    
                    if latest_price:
                        latest_prices.append({
                            'price': latest_price.price,
                            'product_source_id': ps.id,
                            'source_id': ps.source_id
                        })
                
                if not latest_prices:
                    continue
                
                prices = [float(p['price']) for p in latest_prices]
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                
                variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
                stddev = Decimal(str(variance ** 0.5))
                
                best_price_record = min(latest_prices, key=lambda p: float(p['price']))
                
                comparison = self.db.query(PriceComparison).filter(
                    and_(
                        PriceComparison.product_id == product.id,
                        PriceComparison.comparison_date == today
                    )
                ).first()
                
                if not comparison:
                    comparison = PriceComparison(
                        product_id=product.id,
                        comparison_date=today
                    )
                    self.db.add(comparison)
                
                comparison.best_price = Decimal(str(min_price))
                comparison.best_price_source_id = best_price_record['source_id']
                comparison.best_price_product_source_id = best_price_record['product_source_id']
                comparison.min_price = Decimal(str(min_price))
                comparison.max_price = Decimal(str(max_price))
                comparison.price_variance = stddev
                comparison.source_count = len(latest_prices)
                
                self.db.commit()
                results['compared'] += 1
                
            except Exception as e:
                results['errors'].append(f"Error comparing {product.id}: {str(e)}")
        
        return results


class PriceAlertTask(Task):
    """Check price alerts and trigger notifications."""
    
    def execute(self) -> Dict[str, Any]:
        """Check all active price alerts."""
        results = {
            'checked': 0,
            'triggered': 0,
            'errors': []
        }
        
        alerts = self.db.query(PriceAlert).filter(
            PriceAlert.is_active == True
        ).all()
        
        for alert in alerts:
            try:
                latest_prices = self.db.query(Price).join(ProductSource).filter(
                    ProductSource.product_id == alert.product_id,
                    ProductSource.is_active == True
                ).order_by(Price.scraped_at.desc()).all()
                
                if not latest_prices:
                    continue
                
                source_prices = {}
                for price in latest_prices:
                    ps_id = price.product_source_id
                    if ps_id not in source_prices:
                        source_prices[ps_id] = price
                
                triggered = False
                
                if alert.target_price:
                    for price in source_prices.values():
                        if price.price <= alert.target_price:
                            triggered = True
                            break
                
                if alert.price_drop_percentage and not triggered:
                    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
                    old_prices = self.db.query(Price).join(ProductSource).filter(
                        ProductSource.product_id == alert.product_id,
                        Price.scraped_at <= cutoff
                    ).order_by(Price.scraped_at.desc()).limit(len(source_prices)).all()
                    
                    if old_prices:
                        for new_price in source_prices.values():
                            old_price = next(
                                (p for p in old_prices if p.product_source_id == new_price.product_source_id),
                                None
                            )
                            if old_price:
                                drop_pct = float((old_price.price - new_price.price) / old_price.price * 100)
                                if drop_pct >= float(alert.price_drop_percentage):
                                    triggered = True
                                    break
                
                if triggered:
                    alert.last_triggered_at = datetime.now(timezone.utc)
                    alert.trigger_count += 1
                    self.db.commit()
                    results['triggered'] += 1
                
                results['checked'] += 1
                
            except Exception as e:
                results['errors'].append(f"Error checking alert {alert.id}: {str(e)}")
        
        return results

