from unittest.mock import patch


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


def test_download_config_cleanup(app, auth_client, mock_openvpn_dir):
    """Test download config cleanup functionality."""
    from unittest.mock import MagicMock, patch

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
        "ovpn_portal.core.config.Config.ALLOWED_DOMAIN", "test.com", MagicMock
    ), patch("ovpn_portal.core.config.Config.OPENVPN_DIR", mock_openvpn_dir), patch(
        "ovpn_portal.web.routes.vpn.os.unlink"
    ) as mock_unlink, patch(
        "ovpn_portal.web.routes.vpn.send_file", side_effect=mock_send_file
    ):

        # Set up auth mock
        mock_verify.return_value = {"email": "test@test.com", "hd": "test.com"}

        # Change this line to patch the correct method name
        with patch("ovpn_portal.core.vpn.VPNManager.generate_config") as mock_generate:
            mock_generate.return_value = "test config"

            # Make request
            response = auth_client.get(
                "/vpn/download-config",
                headers={"Authorization": "Bearer valid-token"},
            )

            assert response.status_code == 200

            # Consume the response
            _ = b"".join(response.response)
            # Manually execute the cleanup handler
            if cleanup_handler:
                cleanup_handler()

            # Now verify cleanup was called
            mock_unlink.assert_called_once()


def test_download_config_cleanup_scenarios(app, auth_client, mock_openvpn_dir):
    """Test both successful and failed cleanup scenarios."""
    from unittest.mock import patch

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

    # Test Case 1: Successful cleanup
    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify, patch(
        "ovpn_portal.core.config.Config.ALLOWED_DOMAIN", "test.com"
    ), patch("ovpn_portal.core.config.Config.OPENVPN_DIR", mock_openvpn_dir), patch(
        "ovpn_portal.web.routes.vpn.os.unlink"
    ) as mock_unlink, patch(
        "ovpn_portal.web.routes.vpn.send_file", side_effect=mock_send_file
    ), patch(
        "ovpn_portal.core.vpn.VPNManager.generate_config"
    ) as mock_generate:

        mock_verify.return_value = {"email": "test@test.com", "hd": "test.com"}
        mock_generate.return_value = "test config"

        response = auth_client.get(
            "/vpn/download-config",
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 200
        _ = b"".join(response.response)

        if cleanup_handler:
            cleanup_handler()
        mock_unlink.assert_called_once()

    # Test Case 2: Failed cleanup (file already gone)
    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify, patch(
        "ovpn_portal.core.config.Config.ALLOWED_DOMAIN", "test.com"
    ), patch("ovpn_portal.core.config.Config.OPENVPN_DIR", mock_openvpn_dir), patch(
        "ovpn_portal.web.routes.vpn.os.unlink"
    ) as mock_unlink, patch(
        "ovpn_portal.web.routes.vpn.send_file", side_effect=mock_send_file
    ), patch(
        "ovpn_portal.core.vpn.VPNManager.generate_config"
    ) as mock_generate:

        mock_verify.return_value = {"email": "test@test.com", "hd": "test.com"}
        mock_generate.return_value = "test config"
        mock_unlink.side_effect = FileNotFoundError()  # Simulate file already gone

        response = auth_client.get(
            "/vpn/download-config",
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 200
        _ = b"".join(response.response)

        if cleanup_handler:
            cleanup_handler()  # Should not raise an exception
        mock_unlink.assert_called_once()  # Should still have tried to unlink
