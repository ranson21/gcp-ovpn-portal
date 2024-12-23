import pytest


def test_require_auth_no_token(client):
    """Test authentication with no token."""
    response = client.get("/download-config")  # No Authorization header
    assert response.status_code == 401
    assert response.json["error"] == "No authorization token provided"


def test_require_auth_invalid_token_format(client):
    """Test authentication with invalid token format."""
    response = client.get(
        "/download-config", headers={"Authorization": "NotBearer token"}
    )
    assert response.status_code == 401
    assert response.json["error"] == "No authorization token provided"


def test_require_auth_token_verification_fails(client, monkeypatch):
    """Test authentication when token verification fails."""
    from google.oauth2 import id_token

    def mock_verify_token_fails(*args, **kwargs):
        raise ValueError("Invalid token")

    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_verify_token_fails)

    response = client.get(
        "/download-config", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json["error"]


def test_require_auth_invalid_email(client, monkeypatch):
    """Test authentication with invalid domain email."""
    from google.oauth2 import id_token
    from google.auth.transport import requests  # Add this import
    from ovpn_portal.app.config import Config

    def mock_verify_token(*args, **kwargs):
        # Add print statements to see what args we're getting
        print(f"Mock verify called with args: {args}")
        print(f"Mock verify called with kwargs: {kwargs}")
        # This needs to return a complete token with wrong domain
        return {
            "email": "test@wrong-domain.com",
            "iss": "accounts.google.com",
            "aud": (
                args[2] if len(args) > 2 else Config.CLIENT_ID
            ),  # Get the actual client ID passed
            "exp": 1234567890,
            "sub": "12345",
        }

    # We might need to mock the Request class as well
    class MockRequest:
        pass

    monkeypatch.setattr(requests, "Request", MockRequest)
    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_verify_token)

    print(
        f"Config.CLIENT_ID is: {Config.CLIENT_ID}"
    )  # Check what client ID we're using

    response = client.get(
        "/download-config", headers={"Authorization": "Bearer validtoken"}
    )
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.get_json()}")  # See what error we're getting

    assert response.status_code == 403


def test_config_initialization(monkeypatch):
    """Test Config class initialization with different environment configurations."""
    from ovpn_portal.app.config import Config
    import os

    # Store original values
    original_client_id = Config.CLIENT_ID
    original_allowed_domain = Config.ALLOWED_DOMAIN
    original_external_ip = Config.EXTERNAL_IP

    try:
        # Set test values directly on Config class
        monkeypatch.setattr(Config, "CLIENT_ID", "test-client-id")
        monkeypatch.setattr(Config, "ALLOWED_DOMAIN", "test.com")
        monkeypatch.setattr(Config, "EXTERNAL_IP", "1.2.3.4")

        config = Config()
        assert config.CLIENT_ID == "test-client-id"
        assert config.ALLOWED_DOMAIN == "test.com"
        assert config.EXTERNAL_IP == "1.2.3.4"

        # Test warning case
        monkeypatch.setattr(Config, "CLIENT_ID", None)
        config = Config()
        assert config.CLIENT_ID is None

    finally:
        # Restore original values
        Config.CLIENT_ID = original_client_id
        Config.ALLOWED_DOMAIN = original_allowed_domain
        Config.EXTERNAL_IP = original_external_ip


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
