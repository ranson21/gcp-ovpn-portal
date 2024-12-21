import os
from app import Config


def generate_ovpn_config(email):
    """Generate OpenVPN configuration for a user."""
    config = f"""client
dev tun
proto udp
remote {Config.EXTERNAL_IP} 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
auth SHA256
cipher AES-256-CBC
key-direction 1
verb 3
auth-user-pass
auth-nocache

<ca>
{open(os.path.join(Config.OPENVPN_DIR, 'ca.crt')).read()}
</ca>

<cert>
{open(os.path.join(Config.OPENVPN_DIR, 'client.crt')).read()}
</cert>

<key>
{open(os.path.join(Config.OPENVPN_DIR, 'client.key')).read()}
</key>

<tls-auth>
{open(os.path.join(Config.OPENVPN_DIR, 'ta.key')).read()}
</tls-auth>
"""
    return config
