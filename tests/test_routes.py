import pytest


def test_index_no_credential(client):
    """Test POST to index without credential."""
    response = client.post("/")
    assert response.status_code == 302
    assert "error=No+credential+provided" in response.location


def test_app_creation_with_test_config():
    """Test app creation with different test configurations."""
    from ovpn_portal.app import create_app

    # Test with minimal config
    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test-key",
        "VPN_NETWORK": "10.0.0.0/24",
    }

    app = create_app(test_config)
    assert app.secret_key == "test-key"
    assert app.config["VPN_NETWORK"] == "10.0.0.0/24"

    # Test with no config overrides
    app = create_app()
    assert app.secret_key is not None
    assert "VPN_NETWORK" in app.config


def test_download_config_cleanup(app, auth_client, mock_openvpn_dir):
    """Test download config cleanup functionality."""
    import tempfile
    from unittest.mock import patch, MagicMock
    from flask import send_file

    app.config["ALLOWED_DOMAIN"] = "test.com"

    cleanup_handler = None
    original_send_file = send_file

    def mock_send_file(*args, **kwargs):
        response = original_send_file(*args, **kwargs)
        nonlocal cleanup_handler

        def capture_cleanup(func):
            nonlocal cleanup_handler
            cleanup_handler = func
            return func

        response.call_on_close = capture_cleanup
        return response

    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify, patch(
        "ovpn_portal.app.config.Config.ALLOWED_DOMAIN", "test.com"
    ), patch("ovpn_portal.app.config.Config.OPENVPN_DIR", mock_openvpn_dir), patch(
        "ovpn_portal.app.main.routes.os.unlink"
    ) as mock_unlink, patch(
        "ovpn_portal.app.main.routes.send_file", side_effect=mock_send_file
    ):

        # Set up auth mock
        mock_verify.return_value = {"email": "test@test.com", "hd": "test.com"}

        with patch("ovpn_portal.app.main.routes.generate_ovpn_config") as mock_generate:
            mock_generate.return_value = "test config"

            # Make request
            response = auth_client.get(
                "/download-config", headers={"Authorization": "Bearer valid-token"}
            )

            assert response.status_code == 200

            # Consume the response
            _ = b"".join(response.response)

            # Manually execute the cleanup handler
            if cleanup_handler:
                cleanup_handler()

            # Now verify cleanup was called
            mock_unlink.assert_called_once()


def test_download_config_cleanup_error(app, auth_client, mock_openvpn_dir):
    """Test download config cleanup when unlink fails."""
    import tempfile
    from unittest.mock import patch, MagicMock
    from flask import send_file

    app.config["ALLOWED_DOMAIN"] = "test.com"

    cleanup_handler = None
    original_send_file = send_file

    def mock_send_file(*args, **kwargs):
        response = original_send_file(*args, **kwargs)
        nonlocal cleanup_handler

        def capture_cleanup(func):
            nonlocal cleanup_handler
            cleanup_handler = func
            return func

        response.call_on_close = capture_cleanup
        return response

    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify, patch(
        "ovpn_portal.app.config.Config.ALLOWED_DOMAIN", "test.com"
    ), patch("ovpn_portal.app.config.Config.OPENVPN_DIR", mock_openvpn_dir), patch(
        "ovpn_portal.app.main.routes.os.unlink", side_effect=OSError("Test error")
    ) as mock_unlink, patch(
        "ovpn_portal.app.main.routes.send_file", side_effect=mock_send_file
    ):

        # Set up auth mock
        mock_verify.return_value = {"email": "test@test.com", "hd": "test.com"}

        with patch("ovpn_portal.app.main.routes.generate_ovpn_config") as mock_generate:
            mock_generate.return_value = "test config"

            # Make request
            response = auth_client.get(
                "/download-config", headers={"Authorization": "Bearer valid-token"}
            )

            assert response.status_code == 200

            # Consume the response
            _ = b"".join(response.response)

            # Manually execute the cleanup handler
            if cleanup_handler:
                cleanup_handler()

            # Now verify cleanup was attempted
            mock_unlink.assert_called_once()


def test_download_config_error(app, auth_client, mock_openvpn_dir):
    """Test download config with error cases."""
    from ovpn_portal.app.vpn import generate_ovpn_config
    from unittest.mock import patch
    import os

    # Set the allowed domain in app config to match our test email
    app.config["ALLOWED_DOMAIN"] = "test.com"

    # Mock token verification
    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
        # Return a token with email matching the allowed domain
        mock_verify.return_value = {"email": "test@test.com", "hd": "test.com"}

        # Also need to patch the Config class's ALLOWED_DOMAIN
        with patch("ovpn_portal.app.config.Config.ALLOWED_DOMAIN", "test.com"), patch(
            "ovpn_portal.app.config.Config.OPENVPN_DIR", mock_openvpn_dir
        ):

            # Test generate_ovpn_config error
            # Note: Changed the patch path to match where the function is imported in routes.py
            with patch(
                "ovpn_portal.app.main.routes.generate_ovpn_config",
                side_effect=Exception("Test error"),
            ):
                response = auth_client.get(
                    "/download-config", headers={"Authorization": "Bearer valid-token"}
                )
                assert response.status_code == 500
                assert response.get_json()["error"] == "Test error"

            # Test successful case with cleanup error
            with patch(
                "ovpn_portal.app.main.routes.generate_ovpn_config"
            ) as mock_generate:
                mock_generate.return_value = "test config"
                response = auth_client.get(
                    "/download-config", headers={"Authorization": "Bearer valid-token"}
                )
                assert response.status_code == 200


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
