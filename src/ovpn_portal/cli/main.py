import click
from ..core.config import Config
from .commands.serve import serve
from .commands.setup import setup
from .commands.version import version
from .commands.dev import dev


@click.group()
@click.pass_context
def cli(ctx):
    """OpenVPN Client Portal CLI"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config()


cli.add_command(dev)
cli.add_command(serve)
cli.add_command(setup)
cli.add_command(version)
