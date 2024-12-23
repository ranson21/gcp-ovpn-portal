from ovpn_portal.app.vpn import generate_ovpn_config
from ovpn_portal.app.config import Config
from unittest.mock import patch, mock_open
import tempfile
import os

from google.oauth2 import id_token


def test_generate_ovpn_config(app, mock_openvpn_dir):
    """Test OpenVPN config generation."""
    with app.app_context():
        config = generate_ovpn_config("test@test.com")

        # Add assertions to verify config content
        assert "client" in config
        assert "dev tun" in config
        assert "Mock CA Certificate" in config
        assert "Mock Client Certificate" in config
        assert "Mock Client Key" in config
        assert "Mock TLS Auth Key" in config
        assert f"remote {Config.EXTERNAL_IP} 1194" in config


def test_download_config_authenticated(app, mock_openvpn_dir):
    """Test downloading config when authenticated."""
    import os

    # Create a test client
    client = app.test_client()

    # Ensure both app config and Config class have correct domain
    allowed_domain = "test.com"
    app.config["ALLOWED_DOMAIN"] = allowed_domain
    app.config["CLIENT_ID"] = "test-client-id"  # Make sure client ID is set

    # Mock the id_token verification to return a valid user
    mock_idinfo = {
        "email": f"test@{allowed_domain}",
        "hd": allowed_domain,
    }

    # Create a mock config content
    mock_config = "mock OpenVPN config content"

    # Create an actual temporary file for the test
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write(mock_config)
        temp_path = temp_file.name

        with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify, patch(
            "ovpn_portal.app.config.Config.ALLOWED_DOMAIN", allowed_domain
        ), patch("ovpn_portal.app.vpn.generate_ovpn_config", return_value=mock_config):

            # Configure the mock to return our fake user info
            mock_verify.return_value = mock_idinfo

            # Make request with a fake bearer token
            response = client.get(
                "/download-config", headers={"Authorization": "Bearer fake_token_123"}
            )

            if response.status_code != 200:
                print("Response data:", response.get_json())
                print("Mock info:", mock_idinfo)
                print("App config ALLOWED_DOMAIN:", app.config["ALLOWED_DOMAIN"])
                print("Config.ALLOWED_DOMAIN:", Config.ALLOWED_DOMAIN)

            # Verify the response
            assert response.status_code == 200
            assert response.mimetype == "application/x-openvpn-profile"

        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass


def test_download_config_unauthenticated(client):
    """Test downloading config when not authenticated."""
    response = client.get("/download-config")
    assert response.status_code == 401  # Expect Unauthorized instead of redirect
    assert response.get_json() == {"error": "No authorization token provided"}
