from google.auth.transport import requests
from google.oauth2 import id_token


class AuthManager:
    """Manages authentication operations."""

    def __init__(self, config):
        self.config = config

    def verify_token(self, token: str) -> str:
        """Verify Google OAuth token and return email if valid."""
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), self.config.CLIENT_ID)

            email = idinfo.get("email", "")
            if not email.endswith("@" + self.config.ALLOWED_DOMAIN):
                raise ValueError("Invalid email domain")

            return email

        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")
