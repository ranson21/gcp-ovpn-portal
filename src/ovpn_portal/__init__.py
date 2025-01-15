from importlib.metadata import version

try:
    __version__ = version("gcp-ovpn-portal")
except Exception:
    __version__ = "unknown"
