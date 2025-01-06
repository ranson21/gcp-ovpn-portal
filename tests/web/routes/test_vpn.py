import pytest
from unittest.mock import patch
import tempfile
import os


def test_download_config_success(client, auth_headers):
    """Test successful config download."""
    with patch("ovpn_portal.core.auth.AuthManager.verify_token") as mock_auth, patch(
        "ovpn_portal.core.vpn.VPNManager.generate_config"
    ) as mock_vpn:

        mock_auth.return_value = "test@example.com"
        mock_vpn.return_value = "test config"

        response = client.get("/vpn/download-config", headers=auth_headers)
        assert response.status_code == 200
        assert response.mimetype == "application/x-openvpn-profile"


def test_download_config_unauthorized(client):
    """Test config download without authorization."""
    response = client.get("/vpn/download-config")
    assert response.status_code == 401


def test_download_config_error(client, auth_headers):
    """Test config download with error."""
    with patch("ovpn_portal.core.auth.AuthManager.verify_token") as mock_auth, patch(
        "ovpn_portal.core.vpn.VPNManager.generate_config"
    ) as mock_vpn:

        mock_auth.return_value = "test@example.com"
        mock_vpn.side_effect = Exception("Config generation failed")

        response = client.get("/vpn/download-config", headers=auth_headers)
        assert response.status_code == 500
        assert "error" in response.get_json()


def test_vpn_status_connected(client):
    """Test VPN status when connected."""
    client.application.config["VPN_NETWORK"] = "10.8.0.0/24"
    response = client.get("/vpn/status", headers={"X-Forwarded-For": "10.8.0.2"})
    data = response.get_json()
    assert data["connected"] is True
    assert data["client_ip"] == "10.8.0.2"


def test_vpn_status_not_connected(client):
    """Test VPN status when not connected."""
    client.application.config["VPN_NETWORK"] = "10.8.0.0/24"
    response = client.get("/vpn/status", headers={"X-Forwarded-For": "192.168.1.1"})
    data = response.get_json()
    assert data["connected"] is False
    assert data["client_ip"] == "192.168.1.1"


def test_vpn_status_invalid_ip(client):
    """Test VPN status with invalid IP address."""
    response = client.get("/vpn/status", headers={"X-Forwarded-For": "invalid-ip"})
    data = response.get_json()
    assert data["connected"] is False
    assert "error" in data
    assert data["client_ip"] == "invalid-ip"
