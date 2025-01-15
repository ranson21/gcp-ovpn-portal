import click

from ...core.version import get_version


@click.command()
def version():
    """Show version information"""
    ver = get_version()
    click.echo(f"OpenVPN Client Portal v{ver}")
