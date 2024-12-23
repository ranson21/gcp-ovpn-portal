from ovpn_portal.version import get_version
from ovpn_portal.run import create_app
from gunicorn.app.wsgiapp import run as gunicorn_run
import sys

app = create_app()
application = app  # Gunicorn looks for 'application'
version = get_version()


def run_wsgi():
    print(f"Starting ovpn-portal {get_version()}")
    sys.argv = [sys.argv[0], "ovpn_portal.wsgi:application"]
    gunicorn_run()
