from ovpn_portal.app.vpn import (
    generate_ovpn_config,
    check_required_files,
    generate_client_certificates,
)
from ovpn_portal.app.config import Config
from unittest.mock import patch, mock_open
import tempfile
import os

from google.oauth2 import id_token

from unittest.mock import patch, mock_open, call
import subprocess
import pytest
import os


def test_generate_client_certificates_production(app, mock_openvpn_dir):
    """Test certificate generation in production environment."""
    with patch("os.path.exists") as mock_exists, patch("os.chdir") as mock_chdir, patch(
        "subprocess.run"
    ) as mock_run:

        # Mock easy-rsa dir exists (production mode)
        mock_exists.return_value = True

        generate_client_certificates("test@example.com")

        # Verify all subprocess calls were made correctly
        assert mock_chdir.call_args == call("/etc/openvpn/easy-rsa")
        assert len(mock_run.call_args_list) == 4  # Should make 4 subprocess calls

        # Verify the correct commands were run
        expected_commands = [
            ["./easyrsa", "gen-req", "test@example.com", "nopass"],
            ["./easyrsa", "sign-req", "client", "test@example.com"],
            [
                "cp",
                "/etc/openvpn/easy-rsa/pki/issued/test@example.com.crt",
                Config.OPENVPN_DIR,
            ],
            [
                "cp",
                "/etc/openvpn/easy-rsa/pki/private/test@example.com.key",
                Config.OPENVPN_DIR,
            ],
        ]

        for call_args, expected_cmd in zip(mock_run.call_args_list, expected_commands):
            assert call_args[0][0] == expected_cmd


def test_generate_client_certificates_subprocess_error(app, mock_openvpn_dir):
    """Test error handling when subprocess fails."""
    with patch("os.path.exists") as mock_exists, patch("os.chdir") as mock_chdir, patch(
        "subprocess.run"
    ) as mock_run:

        # Mock easy-rsa dir exists (production mode)
        def mock_exists_side_effect(path):
            return path == "/etc/openvpn/easy-rsa"

        mock_exists.side_effect = mock_exists_side_effect

        # Mock subprocess failure
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "test-cmd", output=b"test output", stderr=b"test error"
        )

        with pytest.raises(Exception) as exc_info:
            generate_client_certificates("test@example.com")

        assert "Failed to generate certificates" in str(exc_info.value)


def test_generate_client_certificates_general_error(app, mock_openvpn_dir):
    """Test general error handling in certificate generation."""
    with patch("os.path.exists") as mock_exists, patch("os.chdir") as mock_chdir:

        # Mock easy-rsa dir exists (production mode)
        mock_exists.return_value = True

        # Mock chdir to raise an error
        mock_chdir.side_effect = Exception("General error")

        with pytest.raises(Exception) as exc_info:
            generate_client_certificates("test@example.com")

        assert "Error generating certificates" in str(exc_info.value)


def test_check_required_files_missing_server_files(app, mock_openvpn_dir):
    """Test error when server files are missing."""
    with patch("os.path.exists") as mock_exists:
        # Mock ca.crt missing
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as exc_info:
            check_required_files("test@example.com")

        assert "Required OpenVPN file not found" in str(exc_info.value)


def test_generate_ovpn_config_missing_files(app, mock_openvpn_dir):
    """Test config generation when files need to be generated."""
    test_email = "test@example.com"

    with patch("ovpn_portal.app.vpn.check_required_files") as mock_check:
        mock_check.side_effect = FileNotFoundError("Missing file")

        with pytest.raises(FileNotFoundError):
            generate_ovpn_config(test_email)


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
