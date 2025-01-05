from flask import (
    Blueprint,
    render_template,
    current_app,
    send_from_directory,
    request,
    redirect,
    url_for,
    make_response,
    session,
)
import os
import os
from google.oauth2 import id_token
from google.auth.transport import requests


from ...core.version import get_version

ui_bp = Blueprint("ui", __name__)


@ui_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            credential = request.form.get("credential")
            if not credential:
                return redirect(url_for("ui.index", error="No credential provided"))

            idinfo = id_token.verify_oauth2_token(
                credential, requests.Request(), current_app.config["CLIENT_ID"]
            )
            email = idinfo.get("email", "")

            if not email.endswith("@" + current_app.config["ALLOWED_DOMAIN"]):
                return redirect(url_for("ui.index", error="Invalid domain"))

            # Store in session
            session["email"] = email
            session["token"] = credential

            # Redirect back to the main page
            return redirect(url_for("ui.index"))

        except Exception as e:
            return redirect(url_for("ui.index", error=str(e)))

    # Handle GET request
    error = request.args.get("error")
    response = make_response(
        render_template(
            "index.html",
            client_id=current_app.config["CLIENT_ID"],
            vpn_network=current_app.config.get("VPN_NETWORK", "10.8.0.0/24"),
            app_version=get_version(),
            error=error,
        )
    )
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    return response


@ui_bp.route("/static/<path:path>")
def static_files(path):
    """Serve static files from the frontend build directory."""
    static_dir = current_app.config.get("FRONTEND_DIR")
    if not static_dir:
        static_dir = os.path.join(os.path.dirname(__file__), "..", "static", "dist")
    return send_from_directory(static_dir, path)
