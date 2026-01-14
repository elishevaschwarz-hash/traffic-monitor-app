"""Gunicorn configuration file"""
import logging

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Worker configuration
workers = 1  # Single worker to avoid database/scheduler conflicts
worker_class = "sync"
timeout = 120
keepalive = 5

# Bind
bind = "0.0.0.0:$PORT"

logger = logging.getLogger(__name__)

def on_starting(server):
    """Called just before the master process is initialized."""
    logger.info("Gunicorn is starting...")

def when_ready(server):
    """Called just after the server is started."""
    logger.info("Gunicorn is ready. Spawning workers...")

def post_worker_init(worker):
    """Called just after a worker has been initialized."""
    from models import init_db
    from app import app
    from agents.traffic_monitor import traffic_monitor

    logger.info(f"Worker {worker.pid} initialized, starting app initialization...")

    # Initialize database
    with app.app_context():
        init_db(app)
        logger.info("Database initialized")

    # Start traffic monitoring (only once, in first worker)
    if worker.age == 0:  # First worker
        traffic_monitor.start_monitoring()
        logger.info("Traffic monitoring started")
