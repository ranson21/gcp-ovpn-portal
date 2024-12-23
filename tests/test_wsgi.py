# tests/test_wsgi.py
from ovpn_portal.wsgi import app, application, run_wsgi
import sys


def test_wsgi_app():
    assert app is not None
    assert application is app


def test_run_wsgi(monkeypatch):
    def mock_gunicorn_run():
        pass

    monkeypatch.setattr("ovpn_portal.wsgi.gunicorn_run", mock_gunicorn_run)
    run_wsgi()
    assert sys.argv[1] == "ovpn_portal.wsgi:application"
