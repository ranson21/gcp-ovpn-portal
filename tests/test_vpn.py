import pytest
from ovpn_portal.app.vpn import generate_ovpn_config


def test_generate_ovpn_config(app):
    """Test OpenVPN config generation."""
    with app.app_context():
        config = generate_ovpn_config("test@test.com")

        # Check basic structure
        assert "client" in config
        assert "dev tun" in config
        assert f'remote {app.config["EXTERNAL_IP"]} 1194' in config

        # Check certificates are included
        assert "TEST ca.crt CONTENT" in config
        assert "TEST client.crt CONTENT" in config
        assert "TEST client.key CONTENT" in config
        assert "TEST ta.key CONTENT" in config


def test_download_config_authenticated(auth_client):
    """Test downloading config when authenticated."""
    response = auth_client.get("/download-config")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/x-openvpn-profile"
    assert "client" in response.data.decode()


def test_download_config_unauthenticated(client):
    """Test downloading config when not authenticated."""
    response = client.get("/download-config")
    assert response.status_code == 302  # Redirect to login
