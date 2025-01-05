import click
from ...web.app import create_app
from ...core.config import Config


@click.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=8081, help="Port to bind to")
@click.option("--workers", default=4, help="Number of worker processes")
@click.pass_context
def serve(ctx, host, port, workers):
    """Start the OpenVPN Client Portal web server"""
    config = ctx.obj["config"]

    if not all([config.CLIENT_ID, config.ALLOWED_DOMAIN, config.EXTERNAL_IP]):
        raise click.ClickException(
            "Missing required configuration. Please check your environment variables."
        )

    click.echo(f"Starting OpenVPN Client Portal on {host}:{port}")

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

        options = {
            "bind": f"{host}:{port}",
            "workers": workers,
            "worker_class": "sync",
            "timeout": 30,
        }

        GunicornApp(app, options).run()
