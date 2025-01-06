import pytest
import multiprocessing
from pathlib import Path
import logging
from werkzeug.exceptions import NotFound, HTTPException
from flask import request

from ovpn_portal.core.logging import GunicornLogger


def test_gunicorn_logger_setup(tmp_path):
    """Test GunicornLogger setup with handlers."""

    # Create a mock config class
    class MockConfig:
        def __init__(self):
            self.errorlog = "-"
            self.loglevel = "info"
            self.accesslog = "-"  # Changed from access_log to accesslog
            self.logconfig = None
            self.capture_output = False
            self.syslog = False
            self.syslog_addr = None
            self.syslog_prefix = None
            self.syslog_facility = None
            self.statsd_host = None
            self.statsd_prefix = None
            self.logger_class = None
            self.logconfig_dict = {}

    cfg = MockConfig()
    logger = GunicornLogger(cfg)

    # Modify assertions to handle potential changes in logging setup
    error_handlers = logger.error_log.handlers
    access_handlers = logger.access_log.handlers

    assert any(
        isinstance(h, logging.handlers.RotatingFileHandler) for h in error_handlers
    ), f"No RotatingFileHandler found in error handlers: {error_handlers}"

    assert any(
        isinstance(h, logging.handlers.RotatingFileHandler) for h in access_handlers
    ), f"No RotatingFileHandler found in access handlers: {access_handlers}"


def test_request_formatter_without_context():
    """Test RequestFormatter when not in request context."""
    from ovpn_portal.core.logging import RequestFormatter

    formatter = RequestFormatter()
    record = logging.LogRecord(
        "test_logger", logging.INFO, "test.py", 10, "Test message", (), None
    )

    formatted = formatter.format(record)

    # Verify record attributes were set to None
    assert record.url is None
    assert record.remote_addr is None
    assert record.method is None


def test_handle_404_error(app):
    """Test 404 error handling."""
    with app.test_request_context():
        # Get the handler function
        handler = app.errorhandler(Exception)

        # Create test client
        client = app.test_client()

        # Make a request to a non-existent endpoint
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404
        assert response.get_json() == {
            "error": "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
        }


def test_handle_http_exception(app):
    """Test handling of generic HTTP exceptions."""
    with app.test_request_context():
        # Get the handler function
        handler = app.errorhandler(Exception)

        # Create test client
        client = app.test_client()

        # Use abort to trigger a 400 error
        @app.route("/test-400")
        def test_400():
            from flask import abort

            abort(400)

        # Make the request
        response = client.get("/test-400")

        assert response.status_code == 400
        assert response.get_json() == {
            "error": "400 Bad Request: The browser (or proxy) sent a request that this server could not understand."
        }


def test_start_timer_before_request(app):
    """Test start_timer before_request function."""
    with app.test_request_context("/"):
        app.preprocess_request()
        assert hasattr(request, "start_time")
        assert isinstance(request.start_time, float)


def test_request_formatter_with_context(app):
    """Test RequestFormatter within request context."""
    from ovpn_portal.core.logging import RequestFormatter

    formatter = RequestFormatter()

    with app.test_request_context(
        "/test", method="POST", environ_base={"REMOTE_ADDR": "127.0.0.1"}
    ):
        record = logging.LogRecord(
            "test_logger", logging.INFO, "test.py", 10, "Test message", (), None
        )
        formatted = formatter.format(record)

        # Format the record and verify attributes are set
        formatted_message = formatted  # This triggers the formatter
        assert record.url == request.url
        assert record.method == request.method
        assert record.remote_addr == request.remote_addr


def test_get_gunicorn_options():
    """Test Gunicorn configuration options."""
    from ovpn_portal.core.logging import get_gunicorn_options

    options = get_gunicorn_options()
    expected_workers = multiprocessing.cpu_count() * 2 + 1

    assert options["workers"] == expected_workers
    assert options["worker_class"] == "sync"
    assert options["timeout"] == 30
    assert options["keepalive"] == 2
    assert options["logger_class"] == "ovpn_portal.core.logging.GunicornLogger"
    assert options["accesslog"] == "-"
    assert options["errorlog"] == "-"
    assert "access_log_format" in options
    assert options["loglevel"] == "info"


def test_handle_unhandled_exception(app):
    """Test handling of unhandled exceptions."""
    with app.test_request_context():

        @app.route("/test-error")
        def test_error():
            raise ValueError("Test unhandled error")

        client = app.test_client()
        response = client.get("/test-error")

        assert response.status_code == 500
        assert response.get_json() == {"error": "Internal server error"}
