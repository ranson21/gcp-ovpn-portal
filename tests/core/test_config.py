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


# def test_config_missing_required(monkeypatch):
#     """Test Config initialization with missing required config."""
#     from ovpn_portal.core.config import Config
#     import os

#     # Clear all environment variables
#     for var in ["CLIENT_ID", "ALLOWED_DOMAIN", "EXTERNAL_IP"]:
#         monkeypatch.delenv(var, raising=False)

#     with pytest.raises(ValueError, match="Missing required configurations"):
#         Config()
