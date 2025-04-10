from flask import Flask, request, g, current_app
import time
import os
import psutil
import logging
import json
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class ApplicationMonitor:
    """Monitor application performance and health"""
    
    def __init__(self, app=None):
        self.app = app
        self.stats = {
            'requests': {
                'total': 0,
                'by_endpoint': {},
                'by_method': {},
                'by_status': {},
            },
            'response_times': [],
            'errors': [],
            'last_reset': datetime.now().isoformat()
        }
        self.stats_lock = threading.Lock()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the monitor with the Flask app"""
        self.app = app
        
        # Register before request handler
        @app.before_request
        def before_request():
            g.start_time = time.time()
        
        # Register after request handler
        @app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                endpoint = request.endpoint or 'unknown'
                method = request.method
                status = response.status_code
                
                # Update stats
                with self.stats_lock:
                    self.stats['requests']['total'] += 1
                    
                    # By endpoint
                    if endpoint not in self.stats['requests']['by_endpoint']:
                        self.stats['requests']['by_endpoint'][endpoint] = 0
                    self.stats['requests']['by_endpoint'][endpoint] += 1
                    
                    # By method
                    if method not in self.stats['requests']['by_method']:
                        self.stats['requests']['by_method'][method] = 0
                    self.stats['requests']['by_method'][method] += 1
                    
                    # By status
                    status_str = str(status)
                    if status_str not in self.stats['requests']['by_status']:
                        self.stats['requests']['by_status'][status_str] = 0
                    self.stats['requests']['by_status'][status_str] += 1
                    
                    # Response times (keep last 1000)
                    self.stats['response_times'].append({
                        'timestamp': datetime.now().isoformat(),
                        'endpoint': endpoint,
                        'duration': duration,
                        'method': method,
                        'status': status
                    })
                    if len(self.stats['response_times']) > 1000:
                        self.stats['response_times'] = self.stats['response_times'][-1000:]
            
            return response
        
        # Register error handler
        @app.errorhandler(Exception)
        def handle_error(error):
            with self.stats_lock:
                self.stats['errors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': error.__class__.__name__,
                    'description': str(error),
                    'endpoint': request.endpoint or 'unknown',
                    'method': request.method,
                    'path': request.path
                })
                # Keep last 100 errors
                if len(self.stats['errors']) > 100:
                    self.stats['errors'] = self.stats['errors'][-100:]
            
            # Continue with normal error handling
            raise error
        
        # Register monitoring endpoint
        @app.route('/admin/monitoring', methods=['GET'])
        def monitoring():
            """Admin endpoint for application monitoring"""
            # Check admin authentication
            # (This should be properly protected - implement your auth check)
            
            # Get system stats
            system_stats = self.get_system_stats()
            
            # Combine with application stats
            with self.stats_lock:
                combined_stats = {
                    'application': self.stats,
                    'system': system_stats
                }
            
            return combined_stats
        
        # Register stats reset endpoint
        @app.route('/admin/monitoring/reset', methods=['POST'])
        def reset_stats():
            """Reset monitoring stats"""
            # Check admin authentication
            # (This should be properly protected - implement your auth check)
            
            with self.stats_lock:
                self.reset_stats()
            
            return {'status': 'success', 'message': 'Stats reset successfully'}
    
    def get_system_stats(self):
        """Get system resource statistics"""
        try:
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            
            # Memory info
            memory = psutil.virtual_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'process': {
                    'memory_info': dict(psutil.Process(os.getpid()).memory_info()._asdict()),
                    'cpu_percent': psutil.Process(os.getpid()).cpu_percent(interval=0.1)
                }
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            return {'error': str(e)}
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'requests': {
                'total': 0,
                'by_endpoint': {},
                'by_method': {},
                'by_status': {},
            },
            'response_times': [],
            'errors': [],
            'last_reset': datetime.now().isoformat()
        }

# Add to extensions.py
monitor = ApplicationMonitor()