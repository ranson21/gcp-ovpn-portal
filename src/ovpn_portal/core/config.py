import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration management for OpenVPN Client Portal."""

    def __init__(self):
        self.CLIENT_ID = os.environ.get("CLIENT_ID")
        self.ALLOWED_DOMAIN = os.environ.get("ALLOWED_DOMAIN")
        self.EXTERNAL_IP = os.environ.get("EXTERNAL_IP")
        self.OPENVPN_DIR = os.environ.get("OPENVPN_DIR", "/etc/openvpn")

        # Frontend build directory
        self.FRONTEND_DIR = os.path.join(Path(__file__).parent.parent, "static", "dist")

        # Flask specific configs
        self.SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
        self.SESSION_COOKIE_SECURE = True
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = "Lax"

    def validate(self):
        """Validate required configuration."""
        required = ["CLIENT_ID", "ALLOWED_DOMAIN", "EXTERNAL_IP"]
        missing = [key for key in required if not getattr(self, key)]

        if missing:
            raise ValueError(f"Missing required configurations: {', '.join(missing)}")

    @property
    def is_development(self):
        """Check if running in development mode."""
        return os.environ.get("FLASK_ENV") == "development"
