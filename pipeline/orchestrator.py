"""
Pipeline orchestrator for coordinating tasks.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from .tasks import Task, DiscountAnalysisTask, PriceComparisonTask, PriceAlertTask


class PipelineOrchestrator:
    """Orchestrates pipeline tasks execution."""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.results: Dict[str, Any] = {}
    
    def add_task(self, task: Task):
        """Add a task to the pipeline."""
        self.tasks.append(task)
        return self
    
    def run(self) -> Dict[str, Any]:
        """Execute all tasks in sequence."""
        start_time = datetime.now(timezone.utc)
        results = {
            'started_at': start_time.isoformat(),
            'tasks': [],
            'total_tasks': len(self.tasks),
            'successful': 0,
            'failed': 0
        }
        
        for i, task in enumerate(self.tasks, 1):
            task_name = task.__class__.__name__
            print(f"Running task {i}/{len(self.tasks)}: {task_name}")
            
            try:
                task_result = task.execute()
                results['tasks'].append({
                    'task': task_name,
                    'status': 'success',
                    'result': task_result
                })
                results['successful'] += 1
            except Exception as e:
                results['tasks'].append({
                    'task': task_name,
                    'status': 'failed',
                    'error': str(e)
                })
                results['failed'] += 1
            finally:
                task.close()
        
        results['completed_at'] = datetime.now(timezone.utc).isoformat()
        results['duration_seconds'] = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()
        
        self.results = results
        return results
    
    def run_analytics_pipeline(self) -> Dict[str, Any]:
        """Run complete analytics pipeline."""
        self.tasks = []
        self.add_task(DiscountAnalysisTask())
        self.add_task(PriceComparisonTask())
        self.add_task(PriceAlertTask())
        return self.run()
    
    def run_discount_analysis(self) -> Dict[str, Any]:
        """Run only discount analysis."""
        self.tasks = []
        self.add_task(DiscountAnalysisTask())
        return self.run()
    
    def run_price_comparison(self) -> Dict[str, Any]:
        """Run only price comparison."""
        self.tasks = []
        self.add_task(PriceComparisonTask())
        return self.run()
    
    def run_price_alerts(self) -> Dict[str, Any]:
        """Run only price alerts check."""
        self.tasks = []
        self.add_task(PriceAlertTask())
        return self.run()

