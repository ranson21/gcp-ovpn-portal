from flask import Flask
from flask_cors import CORS
import os
from importlib.resources import files

from .config import Config
from .main import bp as main_bp


def create_app(config_class=Config):
    # Create Flask app with package-aware static and template folders
    app = Flask(
        __name__,
        static_folder=str(files("ovpn_portal") / "static"),
        template_folder=str(files("ovpn_portal") / "templates"),
    )

    # Load config
    app.config.from_object("ovpn_portal.app.config.Config")

    # Add this after creating your Flask app
    CORS(
        app,
        resources={
            r"/*": {
                "origins": ["http://localhost:8081", "http://127.0.0.1:8081"],
                "supports_credentials": True,
            }
        },
    )

    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key-here")
    app.config["VPN_NETWORK"] = os.environ.get("VPN_NETWORK", "10.8.0.0/24")

    # Register blueprints
    app.register_blueprint(main_bp)

    return app
