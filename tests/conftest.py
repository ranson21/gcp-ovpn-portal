import pytest
import tempfile
import os
from pathlib import Path
from ovpn_portal.core.config import Config
from ovpn_portal.web.app import create_app


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    env_vars = {
        "CLIENT_ID": "test-client-id",
        "ALLOWED_DOMAIN": "test.com",
        "EXTERNAL_IP": "1.2.3.4",
        "OPENVPN_DIR": "/tmp/openvpn",
        "SECRET_KEY": "test-key",
        "FLASK_ENV": "development",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def mock_openvpn_dir():
    """Create temporary OpenVPN directory with complete mock structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create easy-rsa directory with PKI structure
        easy_rsa_dir = temp_path / "easy-rsa"
        pki_dir = easy_rsa_dir / "pki"
        issued_dir = pki_dir / "issued"
        private_dir = pki_dir / "private"

        # Create all required directories
        for directory in [easy_rsa_dir, pki_dir, issued_dir, private_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Create mock certificate files
        cert_files = {
            "ca.crt": "Mock CA Certificate",
            "server.crt": "Mock Server Certificate",
            "server.key": "Mock Server Key",
            "ta.key": "Mock TLS Auth Key",
        }

        for filename, content in cert_files.items():
            file_path = temp_path / filename
            file_path.write_text(content)

        # Create mock client certificate files
        test_email = "test@example.com"
        (issued_dir / f"{test_email}.crt").write_text("Mock Client Certificate")
        (private_dir / f"{test_email}.key").write_text("Mock Client Key")

        yield temp_dir


@pytest.fixture
def config(mock_env, mock_openvpn_dir):
    """Create a test configuration."""
    config = Config()
    config.CLIENT_ID = mock_env["CLIENT_ID"]
    config.ALLOWED_DOMAIN = mock_env["ALLOWED_DOMAIN"]
    config.EXTERNAL_IP = mock_env["EXTERNAL_IP"]
    config.OPENVPN_DIR = mock_openvpn_dir
    config.SECRET_KEY = mock_env["SECRET_KEY"]
    return config


@pytest.fixture
def app(config):
    """Create and configure a test application instance."""
    app = create_app()
    # Update both app.config and the config object passed to create_app
    app.config.update(
        {
            "TESTING": True,
            "CLIENT_ID": config.CLIENT_ID,
            "ALLOWED_DOMAIN": config.ALLOWED_DOMAIN,
            "EXTERNAL_IP": config.EXTERNAL_IP,
            "OPENVPN_DIR": config.OPENVPN_DIR,
            "SECRET_KEY": config.SECRET_KEY,
            "VPN_NETWORK": "10.8.0.0/24",
        }
    )
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def mock_google_auth(monkeypatch):
    """Mock Google authentication."""

    def mock_verify_oauth2_token(token, request, client_id):
        if token == "valid-token":
            return {"email": "test@test.com"}
        raise ValueError("Invalid token")

    from google.oauth2 import id_token

    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_verify_oauth2_token)


@pytest.fixture
def mock_template(monkeypatch, tmp_path):
    """Create a mock client.ovpn template file."""
    # Create template file in a temporary location
    template_file = tmp_path / "client.ovpn"

    template_content = """client
dev tun
proto udp
remote {{EXTERNAL_IP}} 1194
resolv-retry infinite
nobind
persist-key
persist-tun

<ca>
{{CA_CERT}}
</ca>

<cert>
{{CLIENT_CERT}}
</cert>

<key>
{{CLIENT_KEY}}
</key>

<tls-auth>
{{TLS_AUTH}}
</tls-auth>
key-direction 1

cipher AES-256-GCM
auth SHA256
verb 3"""

    template_file.write_text(template_content)

    # Patch VPNManager to use our template file
    def mock_generate_config(self, email):
        config = template_file.read_text()
        replacements = {
            "{{EXTERNAL_IP}}": self.config.EXTERNAL_IP,
            "{{CA_CERT}}": (Path(self.config.OPENVPN_DIR) / "ca.crt").read_text(),
            "{{CLIENT_CERT}}": (
                Path(self.config.OPENVPN_DIR) / f"{email}.crt"
            ).read_text(),
            "{{CLIENT_KEY}}": (
                Path(self.config.OPENVPN_DIR) / f"{email}.key"
            ).read_text(),
            "{{TLS_AUTH}}": (Path(self.config.OPENVPN_DIR) / "ta.key").read_text(),
        }

        for key, value in replacements.items():
            config = config.replace(key, value)

        return config

    monkeypatch.setattr(
        "ovpn_portal.core.vpn.VPNManager.generate_config", mock_generate_config
    )

    return template_file


@pytest.fixture
def auth_client(client):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session["email"] = "test@test.com"
        session["token"] = "test-token"
    return client
