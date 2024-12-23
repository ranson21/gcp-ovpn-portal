import pytest


# def test_config_initialization(monkeypatch):
#     """Test Config class initialization with and without CLIENT_ID."""
#     import os
#     from ovpn_portal.app.config import Config

#     # Test with CLIENT_ID set
#     monkeypatch.setenv("CLIENT_ID", "test-client-id")
#     config = Config()
#     assert config.CLIENT_ID == "test-client-id"

#     # Test without CLIENT_ID
#     monkeypatch.delenv("CLIENT_ID")
#     config = Config()
#     assert config.CLIENT_ID is None


def test_require_auth_invalid_token_format(client):
    """Test authentication with invalid token format."""
    response = client.get(
        "/download-config", headers={"Authorization": "Invalid format"}
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "No authorization token provided"


def test_require_auth_token_verification_error(client, monkeypatch):
    """Test authentication when token verification fails."""
    from google.oauth2 import id_token

    def mock_verify_raise_error(*args, **kwargs):
        raise Exception("Token verification failed")

    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_verify_raise_error)

    response = client.get(
        "/download-config", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert "Token verification failed" in response.get_json()["error"]


def test_auth_status_authenticated(auth_client):
    """Test auth status endpoint with authenticated user."""
    response = auth_client.get("/auth-status")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["authenticated"] == True
    assert json_data["email"] == "test@test.com"


def test_auth_status_unauthenticated(client):
    """Test auth status endpoint with unauthenticated user."""
    response = client.get("/auth-status")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["authenticated"] == False


def test_google_auth_success(client, mock_google_auth):
    """Test successful Google authentication."""
    response = client.post("/", data={"credential": "valid-token"})
    assert response.status_code == 302  # Redirect after success


def test_google_auth_failure(client, mock_google_auth):
    """Test failed Google authentication."""
    response = client.post("/", data={"credential": "invalid-token"})
    assert response.status_code == 302  # Redirect with error


def test_google_auth_wrong_domain(client, mock_google_auth, app):
    """Test authentication with wrong email domain."""
    app.config["ALLOWED_DOMAIN"] = "otherdomain.com"
    response = client.post("/", data={"credential": "valid-token"})
    assert response.status_code == 302  # Redirect with error
