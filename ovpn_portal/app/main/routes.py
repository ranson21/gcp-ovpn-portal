from ovpn_portal.version import get_version
from flask import (
    render_template,
    jsonify,
    request,
    send_file,
    current_app,
    redirect,
    url_for,
)
import tempfile
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import make_response
from flask import session

from ..main import bp
from ..middleware import require_auth
from ..vpn import generate_ovpn_config


@bp.route("/auth-status")
def auth_status():
    if "email" in session:
        return jsonify(
            {
                "authenticated": True,
                "email": session["email"],
                "token": session["token"],
            }
        )
    return jsonify({"authenticated": False})


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            credential = request.form.get("credential")
            if not credential:
                return redirect(url_for("main.index", error="No credential provided"))

            idinfo = id_token.verify_oauth2_token(
                credential, requests.Request(), current_app.config["CLIENT_ID"]
            )
            email = idinfo.get("email", "")

            if not email.endswith("@" + current_app.config["ALLOWED_DOMAIN"]):
                return redirect(url_for("main.index", error="Invalid domain"))

            # Store in session
            session["email"] = email
            session["token"] = credential

            # Redirect back to the main page
            return redirect(url_for("main.index"))

        except Exception as e:
            return redirect(url_for("main.index", error=str(e)))

    # Handle GET request
    error = request.args.get("error")
    response = make_response(
        render_template(
            "index.html",
            client_id=current_app.config["CLIENT_ID"],
            vpn_network=current_app.config.get("VPN_NETWORK", "10.8.0.0/24"),
            error=error,
        )
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
            download_name="client.ovpn",
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


@bp.route("/vpn-status")
def vpn_status():
    # Try to get the real IP address from various headers
    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.headers.get("X-Real-IP", "").strip()
        or request.headers.get("CF-Connecting-IP", "").strip()
        or request.remote_addr
    )

    print(client_ip)

    vpn_network = current_app.config.get("VPN_NETWORK", "10.8.0.0/24")

    try:
        # Convert IP and network to ipaddress objects for comparison
        from ipaddress import ip_address, ip_network

        client_ip_obj = ip_address(client_ip)
        vpn_net = ip_network(vpn_network)

        # Check if the IP is in the VPN network range
        is_connected = client_ip_obj in vpn_net

        return jsonify({"connected": is_connected, "client_ip": str(client_ip_obj)})
    except Exception as e:
        return jsonify({"connected": False, "client_ip": client_ip, "error": str(e)})


@bp.route("/health")
def health_check():
    return jsonify({"status": "healthy", "version": get_version()}), 200
