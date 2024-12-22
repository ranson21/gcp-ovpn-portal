import pytest


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
