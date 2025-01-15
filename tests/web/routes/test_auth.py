def test_auth_status_authenticated(client):
    from unittest.mock import patch

    """Test auth status when authenticated."""
    with client.session_transaction() as sess:
        sess["token"] = "valid-token"
        sess["email"] = "test@example.com"

    with patch("ovpn_portal.core.auth.AuthManager.verify_token") as mock_verify:
        mock_verify.return_value = "test@example.com"  # Mock successful verification

        response = client.get("/auth/status")
        data = response.get_json()

        assert response.status_code == 200
        assert data["authenticated"] is True
        assert data["email"] == "test@example.com"


def test_vpn_status_connected(config, client):
    """Test VPN status when connected."""
    config.VPN_NETWORK = "10.8.0.0/24"
    headers = {"X-Real-IP": "10.8.0.2"}  # Use X-Real-IP instead of X-Forwarded-For

    response = client.get("/vpn/status", headers=headers)
    data = response.get_json()

    assert data["connected"] is True
    assert data["client_ip"] == "10.8.0.2"


def test_auth_status_unauthenticated(client):
    """Test auth status when not authenticated."""
    response = client.get("/auth/status")
    data = response.get_json()

    assert response.status_code == 200
    assert data["authenticated"] is False
    assert data["email"] is None


def test_auth_status_invalid_token(client):
    from unittest.mock import patch

    """Test auth status with invalid token."""
    with client.session_transaction() as sess:
        sess["token"] = "invalid-token"

    with patch("ovpn_portal.core.auth.AuthManager.verify_token") as mock_verify:
        mock_verify.side_effect = ValueError("Invalid token")

        response = client.get("/auth/status")
        data = response.get_json()

        assert response.status_code == 200
        assert data["authenticated"] is False
