"""
Simple script to run pipeline tasks.
"""
import sys
from .orchestrator import PipelineOrchestrator


def main():
    """Run pipeline tasks."""
    orchestrator = PipelineOrchestrator()
    
    if len(sys.argv) > 1:
        task_type = sys.argv[1].lower()
        
        if task_type == 'analytics':
            results = orchestrator.run_analytics_pipeline()
        elif task_type == 'discounts':
            results = orchestrator.run_discount_analysis()
        elif task_type == 'comparison':
            results = orchestrator.run_price_comparison()
        elif task_type == 'alerts':
            results = orchestrator.run_price_alerts()
        else:
            print(f"Unknown task type: {task_type}")
            print("Available: analytics, discounts, comparison, alerts")
            return
    else:
        results = orchestrator.run_analytics_pipeline()
    
    print("\n" + "="*50)
    print("Pipeline Execution Results")
    print("="*50)
    print(f"Total tasks: {results['total_tasks']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Duration: {results['duration_seconds']:.2f} seconds")
    print("\nTask Details:")
    
    for task_result in results['tasks']:
        status_icon = "✓" if task_result['status'] == 'success' else "✗"
        print(f"  {status_icon} {task_result['task']}: {task_result['status']}")
        if task_result['status'] == 'success' and 'result' in task_result:
            result = task_result['result']
            for key, value in result.items():
                if key != 'errors' or value:
                    print(f"    - {key}: {value}")


if __name__ == '__main__':
    main()

