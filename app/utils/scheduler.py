from flask import current_app
import threading
import time
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Scheduler for periodic tasks"""
    
    def __init__(self, app=None):
        self.app = app
        self._thread = None
        self._stop_event = threading.Event()
        self.tasks = []
        self.running = False
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize scheduler with Flask app"""
        self.app = app
        
        # Register teardown to stop scheduler
        @app.teardown_appcontext
        def teardown(exception=None):
            self.stop()
    
    def add_task(self, func, interval_seconds, name=None):
        """Add a task to run at regular intervals
        
        Args:
            func: The function to execute
            interval_seconds: Time between executions in seconds
            name: Optional name for the task
        """
        if name is None:
            name = func.__name__
            
        self.tasks.append({
            'func': func,
            'interval': interval_seconds,
            'last_run': None,
            'name': name
        })
        logger.info(f"Task added to scheduler: {name} (every {interval_seconds} seconds)")
        
    def add_daily_task(self, func, time_str, name=None):
        """Add a task to run daily at a specific time
        
        Args:
            func: The function to execute
            time_str: Time to run in format HH:MM (24-hour)
            name: Optional name for the task
        """
        if name is None:
            name = func.__name__
            
        self.tasks.append({
            'func': func,
            'time_str': time_str,
            'last_run': None,
            'name': name,
            'is_daily': True
        })
        logger.info(f"Daily task added to scheduler: {name} (at {time_str})")
    
    def _run_scheduler(self):
        """Run the scheduler in a loop"""
        logger.info("Scheduler thread started")
        while not self._stop_event.is_set():
            now = datetime.now()
            
            for task in self.tasks:
                try:
                    # Handle daily tasks
                    if 'is_daily' in task and task['is_daily']:
                        # Parse time string
                        hour, minute = map(int, task['time_str'].split(':'))
                        run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        
                        # If we've passed the time today and haven't run yet today
                        if now >= run_time and (
                            task['last_run'] is None or 
                            task['last_run'].date() < now.date()
                        ):
                            logger.info(f"Running daily task: {task['name']}")
                            with self.app.app_context():
                                task['func']()
                            task['last_run'] = now
                    
                    # Handle interval tasks
                    elif (
                        task['last_run'] is None or 
                        (now - task['last_run']).total_seconds() >= task['interval']
                    ):
                        logger.info(f"Running scheduled task: {task['name']}")
                        with self.app.app_context():
                            task['func']()
                        task['last_run'] = now
                        
                except Exception as e:
                    logger.error(f"Error in scheduled task {task['name']}: {str(e)}")
            
            # Sleep for a bit to avoid consuming too much CPU
            time.sleep(1)
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
            
        if not self.tasks:
            logger.warning("No tasks registered with scheduler")
            return
            
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._thread.start()
        self.running = True
        logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.running and self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=5)
            self.running = False
            logger.info("Task scheduler stopped")

# Example functions for common maintenance tasks

def clean_temp_files(app):
    """Clean temporary files older than 24 hours"""
    logger.info("Starting temporary file cleanup")
    try:
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        if not os.path.exists(temp_dir):
            logger.info("Temp directory doesn't exist, nothing to clean")
            return
        
        yesterday = datetime.now() - timedelta(hours=24)
        count = 0
        
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            file_modified = datetime.fromtimestamp(os.path.getmtime(item_path))
            
            if file_modified < yesterday:
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    else:
                        import shutil
                        shutil.rmtree(item_path)
                    count += 1
                except Exception as e:
                    logger.error(f"Error removing temp file {item_path}: {str(e)}")
        
        logger.info(f"Cleaned {count} temporary files/directories")
    except Exception as e:
        logger.error(f"Error during temp file cleanup: {str(e)}")