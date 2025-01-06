import pytest
from unittest.mock import patch
from google.oauth2 import id_token


def test_index_get(client):
    """Test index page GET request."""
    response = client.get("/")
    assert response.status_code == 200
    # Check for CLIENT_ID in the script tag instead
    assert b"window.CLIENT_ID" in response.data


def test_index_post_success(client, config, mock_google_auth):
    """Test successful login POST request."""
    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
        # Set up mock to return valid user data
        mock_verify.return_value = {
            "email": f"test@{config.ALLOWED_DOMAIN}",
            "aud": config.CLIENT_ID,
            "iss": "https://accounts.google.com",  # Add required issuer
            "sub": "12345",  # Add subject identifier
        }

        response = client.post("/", data={"credential": "valid-token"})

        # Verify the mock was called correctly
        mock_verify.assert_called_once()

        # Verify response
        assert response.status_code == 302


def test_index_post_invalid_token(client):
    """Test login POST request with invalid token."""
    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.side_effect = ValueError("Invalid token")

        response = client.post("/", data={"credential": "invalid-token"})
        assert response.status_code == 302
        assert "error" in response.location


def test_index_post_invalid_domain(client, config):
    """Test login POST request with invalid domain."""
    with patch("google.oauth2.id_token.verify_oauth2_token") as mock_verify:
        mock_verify.return_value = {
            "email": "test@wrong-domain.com",
            "aud": config.CLIENT_ID,
        }

        response = client.post("/", data={"credential": "valid-token"})
        assert response.status_code == 302
        assert "error" in response.location


def test_static_files(client):
    """Test static file serving."""
    response = client.get("/static/test.txt")
    assert response.status_code == 404  # Or 200 if file exists


def test_index_post_no_credential(client):
    """Test POST request without credential."""
    response = client.post("/")
    assert response.status_code == 302
    assert "error" in response.location


def test_static_files_no_frontend_dir(client, monkeypatch):
    """Test static file serving with no frontend directory."""
    from ovpn_portal.core.config import Config
    import os

    # Clear FRONTEND_DIR
    monkeypatch.setattr(Config, "FRONTEND_DIR", None)

    # Ensure the static file doesn't exist
    static_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "src",
        "ovpn_portal",
        "static",
        "dist",
        "test.txt",
    )
    assert not os.path.exists(static_file)

    response = client.get("/static/test.txt")
    assert response.status_code == 404
