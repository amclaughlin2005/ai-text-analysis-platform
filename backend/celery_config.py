"""
Celery configuration for background job processing
Handles task queues, worker management, and job scheduling
"""

import os
from celery import Celery
from kombu import Queue, Exchange
from app.core.config import get_settings

# Get application settings
settings = get_settings()

# Create Celery application
celery_app = Celery(
    "text_analysis_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.tasks.analysis_tasks',
        'app.tasks.data_processing',
        'app.tasks.report_generation',
        'app.tasks.export_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing and queues
    task_routes={
        'app.tasks.analysis_tasks.*': {'queue': 'analysis'},
        'app.tasks.data_processing.*': {'queue': 'data_processing'},
        'app.tasks.report_generation.*': {'queue': 'reports'},
        'app.tasks.export_tasks.*': {'queue': 'exports'},
    },
    
    # Define queues with different priorities
    task_queues=(
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('analysis', Exchange('analysis'), routing_key='analysis'),
        Queue('data_processing', Exchange('data_processing'), routing_key='data_processing'),
        Queue('reports', Exchange('reports'), routing_key='reports'),
        Queue('exports', Exchange('exports'), routing_key='exports'),
        Queue('high_priority', Exchange('high_priority'), routing_key='high_priority'),
    ),
    
    # Task execution settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    result_expires=3600,  # Results expire after 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Disable prefetching for better load balancing
    worker_max_tasks_per_child=1000,  # Restart workers after 1000 tasks to prevent memory leaks
    worker_concurrency=4,  # Number of concurrent worker processes
    
    # Task time limits
    task_time_limit=3600,  # Hard time limit: 1 hour
    task_soft_time_limit=3000,  # Soft time limit: 50 minutes
    
    # Task retry settings
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker is lost
    
    # Result backend settings
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },
    
    # Task compression
    task_compression='gzip',
    result_compression='gzip',
    
    # Monitoring and logging
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Timezone settings
    timezone='UTC',
    enable_utc=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-expired-cache': {
            'task': 'app.tasks.data_processing.cleanup_expired_cache',
            'schedule': 3600.0,  # Run every hour
            'options': {'queue': 'default'}
        },
        'generate-daily-analytics': {
            'task': 'app.tasks.analysis_tasks.generate_daily_analytics',
            'schedule': 86400.0,  # Run daily
            'options': {'queue': 'analysis'}
        },
        'cleanup-old-jobs': {
            'task': 'app.tasks.data_processing.cleanup_old_analysis_jobs',
            'schedule': 21600.0,  # Run every 6 hours
            'options': {'queue': 'default'}
        }
    },
    
    # Custom configuration
    task_default_queue='default',
    task_default_exchange='default',
    task_default_exchange_type='direct',
    task_default_routing_key='default',
    
    # Redis connection settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Task result settings  
    result_expires=7200,  # Keep results for 2 hours
    result_cache_max=10000,  # Maximum number of results to cache
    
    # Worker settings for production
    worker_disable_rate_limits=True,
    worker_pool_restarts=True,
)

# Configure logging
celery_app.conf.update(
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    worker_log_color=settings.DEBUG,
)

# Task annotations for monitoring and control
celery_app.conf.task_annotations = {
    '*': {
        'rate_limit': '10/s',  # Default rate limit
    },
    'app.tasks.analysis_tasks.process_dataset_with_nltk': {
        'rate_limit': '2/m',  # Limit NLTK processing tasks
        'time_limit': 7200,   # 2 hour time limit for large datasets
        'soft_time_limit': 6600,  # 110 minute soft limit
    },
    'app.tasks.data_processing.upload_to_s3': {
        'rate_limit': '5/m',  # Limit S3 uploads
        'retry_policy': {
            'max_retries': 3,
            'interval_start': 2,
            'interval_step': 2,
            'interval_max': 30,
        },
    },
    'app.tasks.report_generation.generate_executive_report': {
        'rate_limit': '1/m',  # Limit report generation
        'time_limit': 1800,   # 30 minute time limit
    }
}

# Custom task base class
class CallbackTask(celery_app.Task):
    """Custom task base class with callback support for WebSocket updates"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        from app.websocket.manager import connection_manager
        import asyncio
        
        # Extract user_id from task arguments
        user_id = kwargs.get('user_id') or (args[1] if len(args) > 1 else None)
        
        if user_id:
            message = {
                'task_id': task_id,
                'status': 'completed',
                'result': retval,
                'task_name': self.name
            }
            # Note: In production, you might want to use a different mechanism
            # for WebSocket callbacks from Celery tasks
            
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        from app.websocket.manager import connection_manager
        import asyncio
        
        # Extract user_id from task arguments  
        user_id = kwargs.get('user_id') or (args[1] if len(args) > 1 else None)
        
        if user_id:
            message = {
                'task_id': task_id,
                'status': 'failed',
                'error': str(exc),
                'task_name': self.name
            }
            # Note: In production, you might want to use a different mechanism
            # for WebSocket callbacks from Celery tasks
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        from app.websocket.manager import connection_manager
        
        user_id = kwargs.get('user_id') or (args[1] if len(args) > 1 else None)
        
        if user_id:
            message = {
                'task_id': task_id,
                'status': 'retry',
                'error': str(exc),
                'task_name': self.name,
                'retry_count': self.request.retries
            }

# Set the custom task base class
celery_app.Task = CallbackTask

# Health check task
@celery_app.task(bind=True)
def health_check(self):
    """Health check task for monitoring worker status"""
    return {
        'status': 'healthy',
        'worker_id': self.request.id,
        'timestamp': self.request.utc,
        'queue': self.request.delivery_info.get('routing_key', 'unknown')
    }

# Task to test WebSocket integration
@celery_app.task(bind=True)
def test_websocket_integration(self, user_id: str, message: str):
    """Test task for WebSocket integration"""
    import time
    import asyncio
    from app.websocket.manager import connection_manager
    
    # Simulate some work
    for i in range(5):
        time.sleep(1)
        progress = (i + 1) * 20
        
        # Send progress update (in production, use proper async handling)
        update_message = {
            'task_id': self.request.id,
            'status': 'running',
            'progress': progress,
            'message': f"Processing step {i+1}/5: {message}"
        }
    
    return {
        'status': 'completed',
        'message': f'Test task completed: {message}',
        'user_id': user_id
    }

# Utility functions for task management
def get_active_tasks():
    """Get list of active tasks"""
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active()
    return active_tasks

def get_scheduled_tasks():
    """Get list of scheduled tasks"""
    inspect = celery_app.control.inspect()
    scheduled_tasks = inspect.scheduled()
    return scheduled_tasks

def cancel_task(task_id: str):
    """Cancel a running task"""
    celery_app.control.revoke(task_id, terminate=True)

def get_worker_stats():
    """Get worker statistics"""
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    return stats

def purge_queue(queue_name: str):
    """Purge all messages from a queue"""
    celery_app.control.purge()

# Export the celery app
__all__ = ['celery_app', 'health_check', 'test_websocket_integration']
