import pytest
import tempfile
import os

from ovpn_portal.app import create_app
from ovpn_portal.app.config import Config


@pytest.fixture
def mock_openvpn_dir():
    """Create temporary OpenVPN directory with mock certificates."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock certificate files
        cert_files = {
            "ca.crt": "Mock CA Certificate",
            "client.crt": "Mock Client Certificate",
            "client.key": "Mock Client Key",
            "ta.key": "Mock TLS Auth Key",
        }

        for filename, content in cert_files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)

        # Store original directory
        original_dir = Config.OPENVPN_DIR
        # Set config to use temp directory
        Config.OPENVPN_DIR = temp_dir

        yield temp_dir

        # Restore original directory
        Config.OPENVPN_DIR = original_dir


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    # Create a temporary directory for OpenVPN files
    test_vpn_dir = tempfile.mkdtemp()

    # Create dummy OpenVPN files
    files = ["ca.crt", "client.crt", "client.key", "ta.key"]
    for file in files:
        with open(os.path.join(test_vpn_dir, file), "w") as f:
            f.write(f"TEST {file} CONTENT")

    test_config = {
        "TESTING": True,
        "CLIENT_ID": "test-client-id",
        "ALLOWED_DOMAIN": "test.com",
        "EXTERNAL_IP": "1.2.3.4",
        "OPENVPN_DIR": test_vpn_dir,
        "SECRET_KEY": "dev",
    }

    app = create_app(test_config)

    yield app

    # Cleanup
    for file in files:
        os.unlink(os.path.join(test_vpn_dir, file))
    os.rmdir(test_vpn_dir)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session["email"] = "test@test.com"
        session["token"] = "test-token"
    return client


@pytest.fixture
def mock_google_auth(monkeypatch):
    """Mock Google authentication."""

    def mock_verify_oauth2_token(token, request, client_id):
        if token == "valid-token":
            return {"email": "test@test.com"}
        raise ValueError("Invalid token")

    from google.oauth2 import id_token

    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_verify_oauth2_token)
