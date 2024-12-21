# 🔐 OpenVPN Authentication Portal

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A secure, user-friendly authentication portal for OpenVPN configuration distribution. This application provides Google OAuth2 authentication and domain-restricted access to OpenVPN configuration files.

![OpenVPN Auth Portal](docs/images/portal-preview.png)

## 🌟 Features

- 🔒 Secure Google OAuth2 authentication
- 👥 Domain-restricted access control
- 📦 Automated OpenVPN config generation
- 🎨 Clean, responsive web interface
- 🚀 Easy deployment and configuration

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/openvpn-auth-portal
cd openvpn-auth-portal
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
make install
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the development server:
```bash
make run
```

## 🔧 Configuration

The following environment variables are required:

- `CLIENT_ID`: Google OAuth2 client ID
- `ALLOWED_DOMAIN`: Authorized email domain (e.g., "company.com")
- `EXTERNAL_IP`: VPN server's external IP address

## 📁 Project Structure

```
openvpn-auth-portal/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── auth.py
│   └── vpn.py
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── favicon.ico
├── templates/
│   └── index.html
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── Makefile
├── README.md
└── requirements.txt
```

## 🛠️ Development

Run tests:
```bash
make test
```

Format code:
```bash
make format
```

Lint code:
```bash
make lint
```

## 🔒 Security Considerations

- All authentication is performed through Google OAuth2
- Configuration files are generated temporarily and immediately deleted after download
- Domain restriction ensures only authorized users can access the portal
- HTTPS is required in production

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## 👤 Author

Abigail Ranson
- Website: [abbyranson.com](https://abbyranson.com)
- GitHub: [@ranson21](https://github.com/ranson21)