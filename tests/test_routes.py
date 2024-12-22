import pytest


def test_index_page(client):
    """Test the index page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"client_id" in response.data


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
    # Mock a VPN IP address
    client.environ_base["REMOTE_ADDR"] = "10.8.0.2"
    response = client.get("/vpn-status")
    json_data = response.get_json()
    assert json_data["connected"] == True


def test_vpn_status_with_proxy_headers(client):
    """Test VPN status with proxy headers."""
    response = client.get(
        "/vpn-status",
        headers={"X-Forwarded-For": "10.8.0.2, 192.168.1.1", "X-Real-IP": "10.8.0.2"},
    )
    json_data = response.get_json()
    assert json_data["connected"] == True
