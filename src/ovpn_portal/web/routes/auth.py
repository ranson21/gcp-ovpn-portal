from flask import Blueprint, current_app, jsonify, request, session

from ...core.auth import AuthManager
from ...core.config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/status")
def auth_status():
    auth_manager = AuthManager(Config)
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
