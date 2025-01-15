from flask import Blueprint, jsonify

from ...core.version import get_version

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health_check():
    return jsonify({"status": "healthy", "version": get_version()})
