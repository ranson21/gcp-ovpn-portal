import subprocess
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

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
    from unittest.mock import patch

    from ovpn_portal.core.vpn import VPNManager

    config.OPENVPN_DIR = mock_openvpn_dir
    vpn = VPNManager(config)
    email = "new@example.com"

    with patch.object(VPNManager, "_generate_client_certificates") as mock_generate:
        vpn.ensure_client_certificates(email)
        mock_generate.assert_called_once_with(email)


def test_vpn_manager_generate_client_certificates_no_easyrsa(config, mock_openvpn_dir):
    """Test certificate generation when easy-rsa directory doesn't exist."""
    import shutil

    import pytest

    from ovpn_portal.core.vpn import VPNManager

    config.OPENVPN_DIR = mock_openvpn_dir
    vpn = VPNManager(config)
    email = "test@example.com"

    # Remove easy-rsa directory
    shutil.rmtree(vpn.easy_rsa_dir)

    with pytest.raises(RuntimeError, match="easy-rsa directory not found"):
        vpn._generate_client_certificates(email)


def test_generate_client_certificates_file_operations(config, mock_openvpn_dir):
    """Test complete certificate generation including file operations."""
    from unittest.mock import patch

    config.OPENVPN_DIR = mock_openvpn_dir
    vpn = VPNManager(config)
    email = "test@example.com"

    # Create necessary PKI directories
    easy_rsa_dir = Path(mock_openvpn_dir) / "easy-rsa"
    pki_dir = easy_rsa_dir / "pki"
    issued_dir = pki_dir / "issued"
    private_dir = pki_dir / "private"

    for dir in [easy_rsa_dir, pki_dir, issued_dir, private_dir]:
        dir.mkdir(parents=True, exist_ok=True)

    # Create mock certificate files
    (issued_dir / f"{email}.crt").write_text("mock cert")
    (private_dir / f"{email}.key").write_text("mock key")

    # Mock the subprocess calls
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""

        vpn._generate_client_certificates(email)

        # Verify subprocess calls
        assert mock_run.call_count == 2

        # Verify files were copied
        assert (Path(mock_openvpn_dir) / f"{email}.crt").exists()
        assert (Path(mock_openvpn_dir) / f"{email}.key").exists()


def test_generate_client_certificates_file_copy_operations(config, mock_openvpn_dir):
    """Test the file copy operations during certificate generation."""
    vpn = VPNManager(config)
    email = "test@example.com"

    # Set up the directory structure
    pki_dir = Path(mock_openvpn_dir) / "easy-rsa" / "pki"
    issued_dir = pki_dir / "issued"
    private_dir = pki_dir / "private"

    issued_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)

    # Create source certificate files
    test_cert = issued_dir / f"{email}.crt"
    test_key = private_dir / f"{email}.key"
    test_cert.write_text("test cert content")
    test_key.write_text("test key content")

    # Mock the subprocess calls to isolate file operations
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""

        # Run the certificate generation
        vpn._generate_client_certificates(email)

        # Verify files were copied to the correct locations
        dest_cert = Path(config.OPENVPN_DIR) / f"{email}.crt"
        dest_key = Path(config.OPENVPN_DIR) / f"{email}.key"

        assert dest_cert.exists()
        assert dest_key.exists()
        assert dest_cert.read_text() == "test cert content"
        assert dest_key.read_text() == "test key content"


def test_generate_client_certificates_file_error(config, mock_openvpn_dir):
    """Test error handling during file operations in certificate generation."""
    vpn = VPNManager(config)
    email = "test@example.com"

    # Set up minimal directory structure
    easy_rsa_dir = Path(mock_openvpn_dir) / "easy-rsa"
    easy_rsa_dir.mkdir(exist_ok=True)

    # Setup subprocess mock to fail
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            cmd=["./easyrsa", "gen-req", email, "nopass"],
            returncode=1,
            output="mock output",
            stderr="mock error",
        )

        with pytest.raises(RuntimeError) as excinfo:
            vpn._generate_client_certificates(email)

        assert "Certificate generation failed" in str(excinfo.value)


def test_generate_config_missing_files(config, mock_openvpn_dir):
    """Test config generation when required files are missing."""
    import os

    vpn = VPNManager(config)
    email = "test@example.com"

    # Remove required files
    for file in ["ca.crt", "ta.key"]:
        if os.path.exists(os.path.join(mock_openvpn_dir, file)):
            os.remove(os.path.join(mock_openvpn_dir, file))

    with pytest.raises(FileNotFoundError):
        vpn.generate_config(email)


def test_generate_config_template_not_found(config, mock_openvpn_dir):
    """Test config generation when template file is not found."""
    vpn = VPNManager(config)
    email = "test@example.com"

    # First mock subprocess.run to prevent actual command execution
    with patch("subprocess.run") as mock_subprocess:
        # Then mock the template path to a non-existent location
        with patch(
            "pathlib.Path.read_text",
            side_effect=[
                # First read_text call is for template
                FileNotFoundError("Template not found"),
                # Subsequent calls for certificates (these need to succeed)
                "mock ca cert",
                "mock client cert",
                "mock client key",
                "mock tls auth",
            ],
        ):
            with pytest.raises(FileNotFoundError, match="Template not found"):
                vpn.generate_config(email)

            # Verify the mock was used
            assert mock_subprocess.called


def test_generate_config_template_replacements(config, mock_openvpn_dir):
    """Test template replacements in config generation."""
    config.OPENVPN_DIR = mock_openvpn_dir
    config.EXTERNAL_IP = "123.45.67.89"
    vpn = VPNManager(config)
    email = "test@example.com"

    # Create all required files with known content
    test_files = {
        "ca.crt": "MOCK CA CERTIFICATE",
        f"{email}.crt": "MOCK CLIENT CERTIFICATE",
        f"{email}.key": "MOCK CLIENT KEY",
        "ta.key": "MOCK TLS AUTH KEY",
    }

    for filename, content in test_files.items():
        path = Path(mock_openvpn_dir) / filename
        path.write_text(content)

    # Create a mock template with all placeholders
    template_content = """client
remote {{EXTERNAL_IP}} 1194
<ca>
{{CA_CERT}}
</ca>
<cert>
{{CLIENT_CERT}}
</cert>
<key>
{{CLIENT_KEY}}
</key>
<tls-auth>
{{TLS_AUTH}}
</tls-auth>"""

    # Mock the template file read
    with patch("pathlib.Path.read_text") as mock_read:
        # First call returns template, subsequent calls return file contents
        mock_read.side_effect = [
            template_content,  # Template file
            test_files["ca.crt"],
            test_files[f"{email}.crt"],
            test_files[f"{email}.key"],
            test_files["ta.key"],
        ]

        config_content = vpn.generate_config(email)

        # Verify all replacements were made
        assert "remote 123.45.67.89 1194" in config_content
        assert "MOCK CA CERTIFICATE" in config_content
        assert "MOCK CLIENT CERTIFICATE" in config_content
        assert "MOCK CLIENT KEY" in config_content
        assert "MOCK TLS AUTH KEY" in config_content

        # Verify no placeholder remains
        assert "{{" not in config_content
        assert "}}" not in config_content
