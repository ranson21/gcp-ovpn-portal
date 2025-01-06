import click

from ..core.config import Config
from .commands.dev import run_dev
from .commands.serve import serve
from .commands.setup import setup
from .commands.version import version


@click.group()
@click.pass_context
def cli(ctx):
    """OpenVPN Client Portal CLI"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config()


cli.add_command(run_dev)
cli.add_command(serve)
cli.add_command(setup)
cli.add_command(version)
