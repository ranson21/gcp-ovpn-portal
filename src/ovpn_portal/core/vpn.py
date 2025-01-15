# src/ovpn_portal/core/vpn.py
import subprocess
from pathlib import Path


class VPNManager:
    """Manages OpenVPN operations."""

    def __init__(self, config):
        self.config = config
        self.easy_rsa_dir = Path(config.OPENVPN_DIR) / "easy-rsa"

    def ensure_client_certificates(self, email: str) -> None:
        """Ensure client certificates exist, generate if needed."""
        cert_path = Path(self.config.OPENVPN_DIR) / f"{email}.crt"
        key_path = Path(self.config.OPENVPN_DIR) / f"{email}.key"

        if cert_path.exists() and key_path.exists():
            return

        self._generate_client_certificates(email)

    def _generate_client_certificates(self, email: str) -> None:
        """Generate client certificates."""
        if not self.easy_rsa_dir.exists():
            raise RuntimeError("easy-rsa directory not found. Run setup first.")

        try:
            subprocess.run(
                ["./easyrsa", "gen-req", email, "nopass"],
                cwd=self.easy_rsa_dir,
                check=True,
                capture_output=True,
                text=True,
                input=f"{email}\n",
            )

            subprocess.run(
                ["./easyrsa", "sign-req", "client", email],
                cwd=self.easy_rsa_dir,
                check=True,
                capture_output=True,
                text=True,
                input="yes\n",
            )

            # Copy files to OpenVPN directory
            for ext in [".crt", ".key"]:
                src = self.easy_rsa_dir / f"pki/{'issued' if ext == '.crt' else 'private'}/{email}{ext}"
                dst = Path(self.config.OPENVPN_DIR) / f"{email}{ext}"
                dst.write_bytes(src.read_bytes())

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Certificate generation failed: {e.stdout} {e.stderr}")

    def generate_config(self, email: str) -> str:
        """Generate OpenVPN configuration for a user."""
        self.ensure_client_certificates(email)

        # Get the absolute path to the templates directory
        current_file = Path(__file__)  # Get the path of the current file
        template_path = current_file.parent / "templates" / "client.ovpn"

        config = template_path.read_text()

        # Replace placeholders
        replacements = {
            "{{EXTERNAL_IP}}": self.config.EXTERNAL_IP,
            "{{CA_CERT}}": (Path(self.config.OPENVPN_DIR) / "ca.crt").read_text(),
            "{{CLIENT_CERT}}": (Path(self.config.OPENVPN_DIR) / f"{email}.crt").read_text(),
            "{{CLIENT_KEY}}": (Path(self.config.OPENVPN_DIR) / f"{email}.key").read_text(),
            "{{TLS_AUTH}}": (Path(self.config.OPENVPN_DIR) / "ta.key").read_text(),
        }

        for key, value in replacements.items():
            config = config.replace(key, value)

        return config
