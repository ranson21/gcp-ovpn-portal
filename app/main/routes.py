from flask import render_template, jsonify, request, send_file, current_app
import tempfile
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from app.main import bp
from app.auth.routes import require_auth
from app.vpn import generate_ovpn_config
from flask import make_response
from flask import session


@bp.route("/auth-status")
def auth_status():
    if "email" in session:
        return jsonify({"authenticated": True, "email": session["email"]})
    return jsonify({"authenticated": False})


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            credential = request.form.get("credential")
            if not credential:
                return jsonify({"error": "No credential provided"}), 400

            idinfo = id_token.verify_oauth2_token(
                credential, requests.Request(), current_app.config["CLIENT_ID"]
            )
            email = idinfo.get("email", "")

            if not email.endswith("@" + current_app.config["ALLOWED_DOMAIN"]):
                return jsonify({"error": "Invalid domain"}), 403

            # Store in session
            session["email"] = email
            session["token"] = credential

            return jsonify({"success": True, "email": email, "token": credential})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    response = make_response(
        render_template("index.html", client_id=current_app.config["CLIENT_ID"])
    )
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    return response


@bp.route("/download-config")
@require_auth
def download_config(email):
    try:
        config = generate_ovpn_config(email)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ovpn", delete=False
        ) as temp_file:
            temp_file.write(config)
            temp_path = temp_file.name

        # Send the file and then delete it
        return_value = send_file(
            temp_path,
            as_attachment=True,
            attachment_filename="client.ovpn",
            mimetype="application/x-openvpn-profile",
        )

        # Schedule the temporary file for deletion
        @return_value.call_on_close
        def cleanup():
            try:
                os.unlink(temp_path)
            except:
                pass

        return return_value

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200
