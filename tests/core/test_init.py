def test_version_unknown():
    """Test version detection when package is not installed."""
    import sys
    from unittest.mock import patch

    with patch("importlib.metadata.version") as mock_version:
        mock_version.side_effect = Exception("Package not found")

        # Force reload of the module
        if "ovpn_portal" in sys.modules:
            del sys.modules["ovpn_portal"]

        import ovpn_portal

        assert ovpn_portal.__version__ == "unknown"
