from flask import Flask
from flask_cors import CORS
from app.config import Config
import os


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.debug = True
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
    app.config.from_object(config_class)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key-here")
    app.config["VPN_NETWORK"] = os.environ.get("VPN_NETWORK", "10.8.0.0/24")

    # Register blueprints
    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app
