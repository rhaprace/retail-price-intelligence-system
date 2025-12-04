import os
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from pipeline.orchestrator import PipelineOrchestrator
from utils.logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    
    def __init__(self, blocking: bool = False):
        if blocking:
            self.scheduler = BlockingScheduler()
        else:
            self.scheduler = BackgroundScheduler()
        
        self.orchestrator = PipelineOrchestrator()
        self._setup_listeners()
    
    def _setup_listeners(self):
        self.scheduler.add_listener(
            self._job_executed_listener,
            EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(
            self._job_error_listener,
            EVENT_JOB_ERROR
        )
    
    def _job_executed_listener(self, event):
        logger.info(f"Job {event.job_id} executed successfully")
    
    def _job_error_listener(self, event):
        logger.error(f"Job {event.job_id} failed with error: {event.exception}")
    
    def add_analytics_job(
        self,
        hour: int = 2,
        minute: int = 0,
        job_id: str = "analytics_pipeline"
    ):
        self.scheduler.add_job(
            self._run_analytics,
            CronTrigger(hour=hour, minute=minute),
            id=job_id,
            name="Daily Analytics Pipeline",
            replace_existing=True
        )
        logger.info(f"Scheduled analytics pipeline at {hour:02d}:{minute:02d}")
    
    def add_discount_analysis_job(
        self,
        hours: int = 6,
        job_id: str = "discount_analysis"
    ):
        self.scheduler.add_job(
            self._run_discount_analysis,
            IntervalTrigger(hours=hours),
            id=job_id,
            name="Discount Analysis",
            replace_existing=True
        )
        logger.info(f"Scheduled discount analysis every {hours} hours")
    
    def add_price_comparison_job(
        self,
        hours: int = 4,
        job_id: str = "price_comparison"
    ):
        self.scheduler.add_job(
            self._run_price_comparison,
            IntervalTrigger(hours=hours),
            id=job_id,
            name="Price Comparison",
            replace_existing=True
        )
        logger.info(f"Scheduled price comparison every {hours} hours")
    
    def add_alert_check_job(
        self,
        minutes: int = 30,
        job_id: str = "price_alerts"
    ):
        self.scheduler.add_job(
            self._run_price_alerts,
            IntervalTrigger(minutes=minutes),
            id=job_id,
            name="Price Alert Check",
            replace_existing=True
        )
        logger.info(f"Scheduled price alert check every {minutes} minutes")
    
    def add_scraping_job(
        self,
        scraper_func: Callable,
        hours: int = 12,
        job_id: str = "scraping",
        **kwargs
    ):
        self.scheduler.add_job(
            scraper_func,
            IntervalTrigger(hours=hours),
            id=job_id,
            name=f"Scraping Job: {job_id}",
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(f"Scheduled scraping job '{job_id}' every {hours} hours")
    
    def add_custom_job(
        self,
        func: Callable,
        trigger: str,
        job_id: str,
        **trigger_args
    ):
        if trigger == 'cron':
            trigger_obj = CronTrigger(**trigger_args)
        else:
            trigger_obj = IntervalTrigger(**trigger_args)
        
        self.scheduler.add_job(
            func,
            trigger_obj,
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Scheduled custom job '{job_id}'")
    
    def _run_analytics(self):
        logger.info("Starting analytics pipeline...")
        try:
            results = self.orchestrator.run_analytics_pipeline()
            logger.info(f"Analytics pipeline completed: {results['successful']}/{results['total_tasks']} tasks successful")
            return results
        except Exception as e:
            logger.error(f"Analytics pipeline failed: {e}")
            raise
    
    def _run_discount_analysis(self):
        logger.info("Starting discount analysis...")
        try:
            results = self.orchestrator.run_discount_analysis()
            logger.info(f"Discount analysis completed")
            return results
        except Exception as e:
            logger.error(f"Discount analysis failed: {e}")
            raise
    
    def _run_price_comparison(self):
        logger.info("Starting price comparison...")
        try:
            results = self.orchestrator.run_price_comparison()
            logger.info(f"Price comparison completed")
            return results
        except Exception as e:
            logger.error(f"Price comparison failed: {e}")
            raise
    
    def _run_price_alerts(self):
        logger.info("Checking price alerts...")
        try:
            results = self.orchestrator.run_price_alerts()
            logger.info(f"Price alerts check completed")
            return results
        except Exception as e:
            logger.error(f"Price alerts check failed: {e}")
            raise
    
    def remove_job(self, job_id: str):
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job '{job_id}'")
        except Exception as e:
            logger.warning(f"Could not remove job '{job_id}': {e}")
    
    def get_jobs(self) -> list:
        return [
            {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            for job in self.scheduler.get_jobs()
        ]
    
    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Task scheduler started")
    
    def stop(self, wait: bool = True):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Task scheduler stopped")
    
    def pause(self):
        self.scheduler.pause()
        logger.info("Task scheduler paused")
    
    def resume(self):
        self.scheduler.resume()
        logger.info("Task scheduler resumed")


def create_default_scheduler() -> TaskScheduler:
    scheduler = TaskScheduler(blocking=False)
    scheduler.add_analytics_job(hour=2, minute=0)
    scheduler.add_discount_analysis_job(hours=6)
    scheduler.add_price_comparison_job(hours=4)
    scheduler.add_alert_check_job(minutes=30)
    
    return scheduler


def run_scheduler():
    logger.info("Starting Retail Price Intelligence Scheduler")
    
    scheduler = TaskScheduler(blocking=True)
    
    scheduler.add_analytics_job(hour=2, minute=0)
    scheduler.add_discount_analysis_job(hours=6)
    scheduler.add_price_comparison_job(hours=4)
    scheduler.add_alert_check_job(minutes=30)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutdown requested")
        scheduler.stop()


if __name__ == "__main__":
    run_scheduler()
