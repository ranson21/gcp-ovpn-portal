from ovpn_portal.run import create_app
from gunicorn.app.wsgiapp import run as gunicorn_run
import sys

app = create_app()
application = app  # Gunicorn looks for 'application'


def run_wsgi():
    sys.argv = [sys.argv[0], "ovpn_portal.wsgi:application"]
    gunicorn_run()
