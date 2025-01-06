from functools import wraps

from flask import jsonify, request

from ..core.auth import AuthManager
from ..core.config import Config


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "No authorization token provided"}), 401

        token = auth_header.split(" ")[1]
        try:
            auth_manager = AuthManager(Config)
            email = auth_manager.verify_token(token)
            return f(email, *args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    return decorated_function
