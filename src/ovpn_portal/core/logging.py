# src/ovpn_portal/core/logging.py
import logging
import multiprocessing
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import has_request_context, request
from gunicorn.glogging import Logger

from .config import Config


class GunicornLogger(Logger):
    def setup(self, cfg):
        """Configure Gunicorn logging"""
        # Add a default logconfig_json attribute if not present
        if not hasattr(cfg, "logconfig_json"):
            cfg.logconfig_json = None

        super().setup(cfg)
        log_dir = Path(Config.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)

        self.error_log.addHandler(
            RotatingFileHandler(
                log_dir / "gunicorn.error.log",
                maxBytes=10485760,  # 10MB
                backupCount=10,
            )
        )

        self.access_log.addHandler(
            RotatingFileHandler(
                log_dir / "gunicorn.access.log",
                maxBytes=10485760,  # 10MB
                backupCount=10,
            )
        )


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
        return super().format(record)


def get_gunicorn_options():
    """Get Gunicorn configuration options"""
    workers = multiprocessing.cpu_count() * 2 + 1
    return {
        "workers": workers,
        "worker_class": "sync",
        "timeout": 30,
        "keepalive": 2,
        "logger_class": "ovpn_portal.core.logging.GunicornLogger",
        "accesslog": "-",  # Log to stdout
        "errorlog": "-",  # Log to stderr
        "access_log_format": '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s',
        "loglevel": "info",
    }


def setup_logging(app):
    """Configure logging for the application"""
    log_dir = Path(Config.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create formatters
    console_formatter = RequestFormatter(
        "[%(asctime)s] %(remote_addr)s - %(method)s %(url)s\n" "%(levelname)s in %(module)s: %(message)s"
    )
    file_formatter = RequestFormatter(
        "%(asctime)s - %(remote_addr)s - %(method)s - %(url)s - " "%(levelname)s - %(module)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # File handlers
    file_handler = RotatingFileHandler(log_dir / "ovpn-portal.log", maxBytes=10485760, backupCount=10)  # 10MB
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    # Error file handler
    error_file_handler = RotatingFileHandler(
        log_dir / "ovpn-portal.error.log",
        maxBytes=10485760,
        backupCount=10,  # 10MB
    )
    error_file_handler.setFormatter(file_formatter)
    error_file_handler.setLevel(logging.ERROR)

    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_file_handler)

    # Configure gunicorn logging if running under gunicorn
    if "gunicorn" in sys.modules:
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # Request logging
    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def log_request(response):
        if request.path == "/health":  # Skip logging health checks
            return response

        now = time.time()
        duration = round(now - request.start_time, 3)

        log_data = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration": duration,
            "ip": request.remote_addr,
        }

        app.logger.info(
            f"{log_data['method']} {log_data['path']} " f"{log_data['status']} {log_data['duration']}s {log_data['ip']}"
        )

        return response

    # Error logging
    # Error logging
    @app.errorhandler(Exception)
    def handle_exception(e):
        from werkzeug.exceptions import HTTPException, NotFound

        # Handle 404 errors properly
        if isinstance(e, NotFound):
            return {"error": str(e)}, 404

        # Handle other HTTP exceptions
        if isinstance(e, HTTPException):
            return {"error": str(e)}, e.code

        # Log unhandled exceptions
        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return {"error": "Internal server error"}, 500

    return app
