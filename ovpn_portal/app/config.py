import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    CLIENT_ID = os.environ.get("CLIENT_ID")
    ALLOWED_DOMAIN = os.environ.get("ALLOWED_DOMAIN")
    EXTERNAL_IP = os.environ.get("EXTERNAL_IP")
    OPENVPN_DIR = os.environ.get("OPENVPN_DIR", "/etc/openvpn")

    def __init__(self):
        print("Debug - Loading configuration:")
        print(f"CLIENT_ID: {self.CLIENT_ID}")
        print(f"ALLOWED_DOMAIN: {self.ALLOWED_DOMAIN}")
        if not self.CLIENT_ID:
            print("Warning: CLIENT_ID is not set in environment variables")
