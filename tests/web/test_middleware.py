def test_require_auth_invalid_token_format(client):
    """Test authorization with invalid token format."""
    response = client.get(
        "/vpn/download-config", headers={"Authorization": "InvalidFormat"}
    )
    assert response.status_code == 401
    assert response.json["error"] == "No authorization token provided"


def test_require_auth_exception_handling(client):
    """Test authorization with token verification exception."""
    from unittest.mock import patch

    with patch("ovpn_portal.core.auth.AuthManager.verify_token") as mock_verify:
        mock_verify.side_effect = Exception("Verification failed")

        response = client.get(
            "/vpn/download-config", headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert response.json["error"] == "Verification failed"
