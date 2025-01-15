# src/ovpn_portal/cli/commands/dev.py
import os
import subprocess
from pathlib import Path

import click
from honcho.manager import Manager


@click.command()
def run_dev():
    """Run the development server with hot reloading."""
    static_dir = Path(__file__).parent.parent.parent / "static"

    # Check if we need to install npm dependencies
    if not (static_dir / "node_modules").exists():
        click.echo("Installing npm dependencies...")
        subprocess.run(["npm", "install"], cwd=static_dir, check=True)

    # Create a Procfile for honcho
    manager = Manager()

    # Add Flask development server
    os.environ["FLASK_APP"] = "ovpn_portal.web.app:create_app()"
    os.environ["FLASK_ENV"] = "development"
    manager.add_process("flask", "flask run --port 8000 --debug")

    # Add Vite development server
    manager.add_process(
        "vite",
        "npm run dev",  # Removed --prefix since we'll use cwd
        cwd=str(static_dir),  # This ensures Vite runs from the correct directory
    )

    # Start both processes
    click.echo("Starting development servers...")
    manager.loop()

    return manager
