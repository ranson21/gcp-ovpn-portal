from flask import Flask
from flask_cors import CORS

from ..core.logging import setup_logging
from .routes.auth import auth_bp
from .routes.health import health_bp
from .routes.ui import ui_bp
from .routes.vpn import vpn_bp


def create_app(config_object=None):
    app = Flask(
        __name__,
        static_folder="../static/dist",
        template_folder="../static/dist",
    )

    if config_object is None:
        app.config.from_object("ovpn_portal.core.config.Config")
    else:
        app.config.update(config_object)

    # Initialize CORS
    CORS(app)

    # Set up logging
    setup_logging(app)  # Add this line

    # Register blueprints
    app.register_blueprint(ui_bp)  # UI routes first (catch-all should be last)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(vpn_bp, url_prefix="/vpn")
    app.register_blueprint(health_bp)

    return app
