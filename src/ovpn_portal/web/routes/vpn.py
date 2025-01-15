import os
import tempfile

from flask import Blueprint, current_app, jsonify, request, send_file

from ...core.config import Config
from ...core.vpn import VPNManager
from ..middleware import require_auth

vpn_bp = Blueprint("vpn", __name__, url_prefix="/vpn")


@vpn_bp.route("/download-config")
@require_auth
def download_config(email):
    try:
        vpn_manager = VPNManager(Config)
        config = vpn_manager.generate_config(email)

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ovpn", delete=False) as temp_file:
            temp_file.write(config)
            temp_path = temp_file.name

        # Send file and cleanup after
        return_value = send_file(
            temp_path,
            as_attachment=True,
            download_name="client.ovpn",
            mimetype="application/x-openvpn-profile",
        )

        @return_value.call_on_close
        def cleanup():
            try:
                os.unlink(temp_path)
            except Exception:
                pass

        return return_value

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vpn_bp.route("/status")
def vpn_status():
    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.headers.get("X-Real-IP", "").strip()
        or request.headers.get("CF-Connecting-IP", "").strip()
        or request.remote_addr
    )

    vpn_network = current_app.config.get("VPN_NETWORK", "10.8.0.0/24")

    try:
        from ipaddress import ip_address, ip_network

        client_ip_obj = ip_address(client_ip)
        vpn_net = ip_network(vpn_network)

        is_connected = client_ip_obj in vpn_net

        return jsonify({"connected": is_connected, "client_ip": str(client_ip_obj)})
    except Exception as e:
        return jsonify({"connected": False, "client_ip": client_ip, "error": str(e)})
