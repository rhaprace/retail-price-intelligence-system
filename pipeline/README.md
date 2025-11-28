# Pipeline Package

Simple, maintainable pipeline for orchestrating data processing and analytics tasks.

## Structure

- **`orchestrator.py`**: Main pipeline coordinator
- **`tasks.py`**: Individual task implementations
- **`runner.py`**: Command-line runner script

## Tasks

### 1. DiscountAnalysisTask
Analyzes discounts and detects fake discounts by comparing:
- Current price vs historical minimum (30/60/90 days)
- Claimed discount vs actual discount
- Price trends (increasing, decreasing, stable, volatile)

### 2. PriceComparisonTask
Compares prices across multiple sources for each product:
- Finds best price
- Calculates price variance
- Tracks source count

### 3. PriceAlertTask
Checks price alerts and triggers notifications:
- Target price alerts
- Percentage drop alerts

## Usage

### Programmatic Usage

```python
from pipeline import PipelineOrchestrator

orchestrator = PipelineOrchestrator()
results = orchestrator.run_analytics_pipeline()

results = orchestrator.run_discount_analysis()
results = orchestrator.run_price_comparison()
results = orchestrator.run_price_alerts()

orchestrator = PipelineOrchestrator()
orchestrator.add_task(DiscountAnalysisTask())
orchestrator.add_task(PriceComparisonTask())
results = orchestrator.run()
```

### Command Line Usage

```bash
python -m pipeline.runner
python -m pipeline.runner analytics
python -m pipeline.runner discounts
python -m pipeline.runner comparison
python -m pipeline.runner alerts
```

## Task Execution Flow

```
1. DiscountAnalysisTask
   ↓
   Analyze all product sources
   Calculate 30/60/90 day metrics
   Detect fake discounts
   ↓
2. PriceComparisonTask
   ↓
   Compare prices across sources
   Find best prices
   Calculate variance
   ↓
3. PriceAlertTask
   ↓
   Check active alerts
   Trigger notifications
```

## Output

Each task returns a dictionary with:
- Success/failure counts
- Processed items count
- Errors (if any)
- Task-specific metrics

## Integration with Scrapers

The pipeline is designed to run after scraping:
1. Scrapers collect price data → `prices` table
2. Pipeline runs analytics → `discount_analysis`, `price_comparisons` tables
3. Alerts are checked → `price_alerts` table updated

## Scheduling

For production, you can schedule pipeline runs using:
- Cron jobs (Linux/Mac)
- Task Scheduler (Windows)
- Celery/APScheduler (Python)
- Airflow/Prefect (Advanced)

Example cron (daily at 2 AM):
```
0 2 * * * cd /path/to/project && python -m pipeline.runner analytics
```

