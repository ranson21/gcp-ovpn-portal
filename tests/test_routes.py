import pytest


def test_index_no_credential(client):
    """Test POST to index without credential."""
    response = client.post("/")
    assert response.status_code == 302
    assert "error=No+credential+provided" in response.location


# def test_download_config_error(app, auth_client):
#     """Test download config with error."""
#     from ovpn_portal.app.vpn import generate_ovpn_config
#     from unittest.mock import patch

#     with patch(
#         "ovpn_portal.app.vpn.generate_ovpn_config", side_effect=Exception("Test error")
#     ):
#         response = auth_client.get(
#             "/download-config", headers={"Authorization": "Bearer valid-token"}
#         )
#         assert response.status_code == 500
#         assert response.get_json()["error"] == "Test error"


def test_vpn_status_invalid_ip(client):
    """Test VPN status with invalid IP address."""
    response = client.get("/vpn-status", headers={"X-Forwarded-For": "invalid-ip"})
    json_data = response.get_json()
    assert not json_data["connected"]
    assert "error" in json_data


def test_index_page(client):
    """Test the index page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"window.CLIENT_ID" in response.data


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_vpn_status_not_connected(client):
    """Test VPN status when not connected."""
    response = client.get("/vpn-status")
    json_data = response.get_json()
    assert "connected" in json_data
    assert "client_ip" in json_data


def test_vpn_status_connected(client):
    """Test VPN status when connected through VPN."""
    # Mock the config to match the application's VPN network
    client.application.config["VPN_NETWORK"] = "34.42.0.0/16"  # Using /16 subnet
    # Use an IP from the correct VPN network
    client.environ_base["REMOTE_ADDR"] = "34.42.0.2"
    response = client.get("/vpn-status")
    json_data = response.get_json()
    assert json_data["connected"] == True


def test_vpn_status_with_proxy_headers(client):
    """Test VPN status with proxy headers."""
    # Mock the config to match the application's VPN network
    client.application.config["VPN_NETWORK"] = "34.42.0.0/16"  # Using /16 subnet
    response = client.get(
        "/vpn-status",
        headers={"X-Forwarded-For": "34.42.0.2, 192.168.1.1", "X-Real-IP": "34.42.0.2"},
    )
    json_data = response.get_json()
    assert json_data["connected"] == True
