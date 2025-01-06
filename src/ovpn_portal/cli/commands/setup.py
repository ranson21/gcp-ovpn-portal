import os
import subprocess

import click


@click.command()
@click.option("--force", is_flag=True, help="Force setup even if already configured")
@click.pass_context
def setup(ctx, force):
    """Initialize OpenVPN configuration"""
    config = ctx.obj["config"]

    if not os.path.exists(config.OPENVPN_DIR) or force:
        click.echo("Setting up OpenVPN configuration...")

        # Create OpenVPN directory if it doesn't exist
        os.makedirs(config.OPENVPN_DIR, exist_ok=True)

        # Initialize easy-rsa
        easy_rsa_dir = os.path.join(config.OPENVPN_DIR, "easy-rsa")
        if not os.path.exists(easy_rsa_dir) or force:
            click.echo("Initializing easy-rsa...")
            os.makedirs(easy_rsa_dir, exist_ok=True)
            subprocess.run(["easyrsa", "init-pki"], cwd=easy_rsa_dir, check=True)

        # Generate CA if it doesn't exist
        if not os.path.exists(os.path.join(config.OPENVPN_DIR, "ca.crt")) or force:
            click.echo("Generating CA certificate...")
            subprocess.run(["easyrsa", "build-ca"], cwd=easy_rsa_dir, check=True)

        # Generate server certificates
        if not os.path.exists(os.path.join(config.OPENVPN_DIR, "server.crt")) or force:
            click.echo("Generating server certificates...")
            subprocess.run(
                ["easyrsa", "build-server-full", "server"],
                cwd=easy_rsa_dir,
                check=True,
            )

        # Generate ta.key if it doesn't exist
        if not os.path.exists(os.path.join(config.OPENVPN_DIR, "ta.key")) or force:
            click.echo("Generating ta.key...")
            subprocess.run(
                ["openvpn", "--genkey", "--secret", "ta.key"],
                cwd=config.OPENVPN_DIR,
                check=True,
            )

        click.echo("OpenVPN configuration setup complete!")
    else:
        click.echo("OpenVPN configuration already exists. Use --force to recreate.")
