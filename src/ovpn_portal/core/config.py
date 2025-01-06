import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration management for OpenVPN Client Portal."""

    CLIENT_ID = os.environ.get("CLIENT_ID")
    ALLOWED_DOMAIN = os.environ.get("ALLOWED_DOMAIN")
    EXTERNAL_IP = os.environ.get("EXTERNAL_IP")
    OPENVPN_DIR = os.environ.get("OPENVPN_DIR", "/etc/openvpn")
    VPN_NETWORK = os.environ.get("VPN_NETWORK", "10.8.0.0/24")
    LOG_DIR = os.environ.get("LOG_DIR", "/var/log/ovpn-portal")  # Add this line

    # Frontend build directory
    FRONTEND_DIR = os.path.join(Path(__file__).parent.parent, "static", "dist")

    # Flask specific configs
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    def __init__(self):
        """Validate required configuration."""
        required = ["CLIENT_ID", "ALLOWED_DOMAIN", "EXTERNAL_IP"]
        missing = [key for key in required if not getattr(self, key)]

        if missing:
            raise ValueError(f"Missing required configurations: {', '.join(missing)}")

    @property
    def is_development(self):
        """Check if running in development mode."""
        return os.environ.get("FLASK_ENV") == "development"
