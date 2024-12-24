import os
from .config import Config


def generate_ovpn_config(email):
    """Generate OpenVPN configuration for a user."""
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
tls-auth ta.key 1  # Note this is 1, not 0 like the server
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
