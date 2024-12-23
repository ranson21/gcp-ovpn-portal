from flask import Flask
from flask_cors import CORS
import os
from importlib.resources import files

from .config import Config
from .main import bp as main_bp


def create_app(test_config=None):
    # Create Flask app with package-aware static and template folders
    app = Flask(
        __name__,
        static_folder=str(files("ovpn_portal") / "static"),
        template_folder=str(files("ovpn_portal") / "templates"),
    )

    # Load default config first
    app.config.from_object("ovpn_portal.app.config.Config")

    # Override with test config if provided
    if test_config is not None:
        app.config.update(test_config)

    # Add CORS after creating Flask app
    CORS(
        app,
        resources={
            r"/*": {
                "origins": ["http://localhost:8081", "http://127.0.0.1:8081"],
                "supports_credentials": True,
            }
        },
    )

    # Set secret key and VPN network only if not in test config
    if test_config is None or "SECRET_KEY" not in test_config:
        app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key-here")
    if test_config is None or "VPN_NETWORK" not in test_config:
        app.config["VPN_NETWORK"] = os.environ.get("VPN_NETWORK", "10.8.0.0/24")

    # Register blueprints
    app.register_blueprint(main_bp)

    return app
