from flask import Blueprint, jsonify, request, session, current_app
from ...core.auth import AuthManager

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/status")
def auth_status():
    return jsonify(
        {
            "authenticated": "email" in session,
            "email": session.get("email"),
            "token": session.get("token"),
        }
    )


@auth_bp.route("/google", methods=["POST"])
def google_auth():
    try:
        credential = request.form.get("credential")
        if not credential:
            return jsonify({"error": "No credential provided"}), 400

        auth_manager = AuthManager(current_app.config)
        email = auth_manager.verify_token(credential)

        session["email"] = email
        session["token"] = credential

        return jsonify({"success": True, "email": email, "token": credential})

    except Exception as e:
        return jsonify({"error": str(e)}), 401
