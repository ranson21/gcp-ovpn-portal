import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
import subprocess
from ovpn_portal.core.vpn import VPNManager


def test_vpn_manager_init(config):
    """Test VPNManager initialization."""
    vpn = VPNManager(config)
    assert vpn.config == config
    assert vpn.easy_rsa_dir == Path(config.OPENVPN_DIR) / "easy-rsa"


def test_ensure_client_certificates_existing(config, mock_openvpn_dir):
    """Test ensure_client_certificates when certificates exist."""
    config.OPENVPN_DIR = mock_openvpn_dir
    vpn = VPNManager(config)
    email = "test@example.com"

    # Create mock certificate files
    cert_path = Path(mock_openvpn_dir) / f"{email}.crt"
    key_path = Path(mock_openvpn_dir) / f"{email}.key"
    cert_path.touch()
    key_path.touch()

    # Should not raise any exceptions
    vpn.ensure_client_certificates(email)


def test_generate_client_certificates(config, mock_openvpn_dir):
    """Test client certificate generation."""
    config.OPENVPN_DIR = mock_openvpn_dir
    vpn = VPNManager(config)
    email = "test@example.com"

    with patch("subprocess.run") as mock_run:
        vpn._generate_client_certificates(email)

        assert mock_run.call_count == 2


def test_generate_client_certificates_error(config, mock_openvpn_dir):
    """Test certificate generation error handling."""
    config.OPENVPN_DIR = mock_openvpn_dir
    vpn = VPNManager(config)
    email = "test@example.com"

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", output="error")

        with pytest.raises(RuntimeError, match="Certificate generation failed"):
            vpn._generate_client_certificates(email)


def test_generate_config(config, mock_openvpn_dir, mock_template):
    """Test OpenVPN config generation."""
    config.OPENVPN_DIR = mock_openvpn_dir
    vpn = VPNManager(config)
    email = "test@example.com"

    # Create mock certificate files
    mock_files = {
        "ca.crt": "mock CA cert",
        f"{email}.crt": "mock client cert",
        f"{email}.key": "mock client key",
        "ta.key": "mock TLS auth key",
    }

    for filename, content in mock_files.items():
        path = Path(mock_openvpn_dir) / filename
        path.write_text(content)

    config_content = vpn.generate_config(email)

    # Verify the config contains the expected values
    assert f"remote {config.EXTERNAL_IP}" in config_content
    assert "mock CA cert" in config_content
    assert "mock client cert" in config_content
    assert "mock client key" in config_content
    assert "mock TLS auth key" in config_content


def test_vpn_manager_ensure_client_certificates_not_exists(config, mock_openvpn_dir):
    """Test ensure_client_certificates when certificates don't exist."""
    from ovpn_portal.core.vpn import VPNManager
    from unittest.mock import patch

    config.OPENVPN_DIR = mock_openvpn_dir
    vpn = VPNManager(config)
    email = "new@example.com"

    with patch.object(VPNManager, "_generate_client_certificates") as mock_generate:
        vpn.ensure_client_certificates(email)
        mock_generate.assert_called_once_with(email)


def test_vpn_manager_generate_client_certificates_no_easyrsa(config, mock_openvpn_dir):
    """Test certificate generation when easy-rsa directory doesn't exist."""
    from ovpn_portal.core.vpn import VPNManager
    import shutil
    import pytest

    config.OPENVPN_DIR = mock_openvpn_dir
    vpn = VPNManager(config)
    email = "test@example.com"

    # Remove easy-rsa directory
    shutil.rmtree(vpn.easy_rsa_dir)

    with pytest.raises(RuntimeError, match="easy-rsa directory not found"):
        vpn._generate_client_certificates(email)
