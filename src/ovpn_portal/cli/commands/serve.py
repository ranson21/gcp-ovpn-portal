import click

from ...core.cli import print_openvpn_logo
from ...core.logging import get_gunicorn_options
from ...web.app import create_app


@click.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=8081, help="Port to bind to")
@click.option("--workers", default=4, help="Number of worker processes")
@click.pass_context
def serve(ctx, host, port, workers):
    """Start the OpenVPN Client Portal web server"""
    config = ctx.obj["config"]

    if not all([config.CLIENT_ID, config.ALLOWED_DOMAIN, config.EXTERNAL_IP]):
        raise click.ClickException("Missing required configuration. Please check your environment variables.")

    click.echo(print_openvpn_logo())

    app = create_app()

    if app.debug:
        app.run(host=host, port=port)
    else:
        from gunicorn.app.base import BaseApplication

        class GunicornApp(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = get_gunicorn_options()
        if workers:
            options["workers"] = workers
        options["bind"] = f"{host}:{port}"

        GunicornApp(app, options).run()
