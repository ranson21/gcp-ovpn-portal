from unittest.mock import patch

import pytest
from google.auth.transport import requests
from google.oauth2 import id_token

from ovpn_portal.core.auth import AuthManager


def test_auth_manager_init(config):
    """Test AuthManager initialization."""
    auth = AuthManager(config)
    assert auth.config == config


def test_verify_token_success(config):
    """Test successful token verification."""
    auth = AuthManager(config)

    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {
            "email": f"test@{config.ALLOWED_DOMAIN}",
            "aud": config.CLIENT_ID,
        }

        email = auth.verify_token("valid-token")
        assert email == f"test@{config.ALLOWED_DOMAIN}"


def test_verify_token_invalid_domain(config):
    """Test token verification with invalid domain."""
    auth = AuthManager(config)

    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {
            "email": "test@wrong-domain.com",
            "aud": config.CLIENT_ID,
        }

        with pytest.raises(ValueError, match="Invalid email domain"):
            auth.verify_token("valid-token")


def test_verify_token_verification_error(config):
    """Test token verification with verification error."""
    auth = AuthManager(config)

    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.side_effect = ValueError("Invalid token")

        with pytest.raises(ValueError, match="Token verification failed"):
            auth.verify_token("invalid-token")
