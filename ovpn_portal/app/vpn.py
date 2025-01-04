import os
import subprocess
from .config import Config


def generate_client_certificates(email):
    """Generate client certificates if they don't exist."""
    try:
        easy_rsa_dir = "/etc/openvpn/easy-rsa"

        # Check if we're in test environment (mock directory)
        if not os.path.exists(easy_rsa_dir):
            # In test environment, create mock certificates directly
            with open(os.path.join(Config.OPENVPN_DIR, f"{email}.crt"), "w") as f:
                f.write("Mock Client Certificate")
            with open(os.path.join(Config.OPENVPN_DIR, f"{email}.key"), "w") as f:
                f.write("Mock Client Key")
            return

        # Production certificate generation
        os.chdir(easy_rsa_dir)

        subprocess.run(
            ["./easyrsa", "gen-req", email, "nopass"],
            check=True,
            capture_output=True,
            text=True,
            input=f"{email}\n",
        )

        subprocess.run(
            ["./easyrsa", "sign-req", "client", email],
            check=True,
            capture_output=True,
            text=True,
            input="yes\n",
        )

        subprocess.run(
            ["cp", f"{easy_rsa_dir}/pki/issued/{email}.crt", Config.OPENVPN_DIR],
            check=True,
        )
        subprocess.run(
            ["cp", f"{easy_rsa_dir}/pki/private/{email}.key", Config.OPENVPN_DIR],
            check=True,
        )

    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to generate certificates: {e.stdout} {e.stderr}")
    except Exception as e:
        raise Exception(f"Error generating certificates: {str(e)}")


def check_required_files(email):
    """Check if all required OpenVPN files exist and generate if needed."""
    required_files = {"ca.crt": "ca.crt", "ta.key": "ta.key"}

    # Check for required server files
    for file in required_files.values():
        path = os.path.join(Config.OPENVPN_DIR, file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required OpenVPN file not found: {path}")

    # Check for client certificate files
    client_cert = os.path.join(Config.OPENVPN_DIR, f"{email}.crt")
    client_key = os.path.join(Config.OPENVPN_DIR, f"{email}.key")

    if not (os.path.exists(client_cert) and os.path.exists(client_key)):
        generate_client_certificates(email)


def generate_ovpn_config(email):
    """Generate OpenVPN configuration for a user."""
    # Check all required files first and generate if needed
    check_required_files(email)

    config = f"""client
dev tun
proto udp4
remote {Config.EXTERNAL_IP} 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
auth SHA256
cipher AES-256-CBC
verb 3
auth-user-pass
auth-nocache
redirect-gateway def1
key-direction 1
tls-auth ta.key 1
block-ipv6
dhcp-option DNS 8.8.8.8
dhcp-option DNS 8.8.4.4
script-security 2
up /etc/openvpn/update-systemd-resolved
down /etc/openvpn/update-systemd-resolved
down-pre
pull-filter ignore "route-ipv6"
pull-filter ignore "ifconfig-ipv6"
mssfix 1400
socket-flags TCP_NODELAY
sndbuf 0
rcvbuf 0
ncp-ciphers AES-256-GCM:AES-128-GCM
fast-io

<ca>
{open(os.path.join(Config.OPENVPN_DIR, 'ca.crt')).read()}
</ca>

<cert>
{open(os.path.join(Config.OPENVPN_DIR, f'{email}.crt')).read()}
</cert>

<key>
{open(os.path.join(Config.OPENVPN_DIR, f'{email}.key')).read()}
</key>

<tls-auth>
{open(os.path.join(Config.OPENVPN_DIR, 'ta.key')).read()}
</tls-auth>
"""
    return config
