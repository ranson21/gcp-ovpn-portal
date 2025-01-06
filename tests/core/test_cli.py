from unittest.mock import patch

from ovpn_portal.core.cli import print_openvpn_logo


def test_print_openvpn_logo():
    """Test that the OpenVPN logo is correctly formatted with version."""
    with patch("ovpn_portal.core.cli.get_version") as mock_version:
        # Set a mock version
        mock_version.return_value = "1.0.0"

        # Get the logo
        logo = print_openvpn_logo()

        # Verify the logo contains the version
        assert "OpenVPN Client Portal v1.0.0" in logo

        # Verify the ASCII art is present
        assert "▒▒▒▒▒▒▒▒▒▒▒▒▒▒" in logo
        assert "████" in logo


def test_print_openvpn_logo_version_error():
    """Test logo generation when version retrieval fails."""
    with patch("ovpn_portal.core.cli.get_version") as mock_version:
        # Simulate a version retrieval error
        mock_version.side_effect = Exception("Version error")

        # The function should return a string with 'unknown' version
        logo = print_openvpn_logo()

        # Verify the logo contains 'unknown' version
        assert "OpenVPN Client Portal vunknown" in logo

        # Basic structure should still be present
        assert "▒▒▒▒▒▒▒▒▒▒▒▒▒▒" in logo
        assert "████" in logo
