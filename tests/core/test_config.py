import pytest


def test_config_development_mode(monkeypatch):
    """Test Config.is_development property."""
    from ovpn_portal.core.config import Config

    # Test development mode
    monkeypatch.setenv("FLASK_ENV", "development")
    config = Config()
    assert config.is_development is True

    # Test non-development mode
    monkeypatch.setenv("FLASK_ENV", "production")
    config = Config()
    assert config.is_development is False


def test_config_missing_required(monkeypatch):
    """Test Config initialization with missing required config."""
    from ovpn_portal.core.config import Config

    # Patch the class attributes directly
    original_client_id = Config.CLIENT_ID
    original_allowed_domain = Config.ALLOWED_DOMAIN
    original_external_ip = Config.EXTERNAL_IP

    try:
        Config.CLIENT_ID = None
        Config.ALLOWED_DOMAIN = None
        Config.EXTERNAL_IP = None

        with pytest.raises(ValueError, match="Missing required configurations"):
            Config()
    finally:
        # Restore original values
        Config.CLIENT_ID = original_client_id
        Config.ALLOWED_DOMAIN = original_allowed_domain
        Config.EXTERNAL_IP = original_external_ip
