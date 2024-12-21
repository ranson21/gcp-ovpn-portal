from flask import jsonify, request
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
from app.auth import bp
from app import Config


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "No authorization token provided"}), 401

        token = auth_header.split(" ")[1]
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), Config.CLIENT_ID
            )

            email = idinfo.get("email", "")
            if not email.endswith("@" + Config.ALLOWED_DOMAIN):
                return jsonify({"error": "Invalid domain"}), 403

            return f(email, *args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    return decorated_function


@bp.route("/auth", methods=["POST"])
def authenticate():
    try:
        token = request.form.get("token")
        if not token:
            return jsonify({"error": "No token provided"}), 400

        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), Config.CLIENT_ID
        )

        email = idinfo.get("email", "")
        if not email.endswith("@" + Config.ALLOWED_DOMAIN):
            return jsonify({"error": "Invalid domain"}), 403

        return jsonify({"success": True, "email": email}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
