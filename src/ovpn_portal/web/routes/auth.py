from flask import Blueprint, jsonify, request, session, current_app
from ...core.auth import AuthManager

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/status")
def auth_status():
    auth_manager = AuthManager(current_app.config)
    authenticated = False

    if session.get("token") != None:
        try:
            auth_manager.verify_token(session.get("token"))
            authenticated = True
        except:
            authenticated = False

    return jsonify(
        {
            "authenticated": authenticated,
            "email": session.get("email"),
            "token": session.get("token"),
        }
    )
