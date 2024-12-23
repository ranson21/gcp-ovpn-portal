from ovpn_portal.app import create_app


def validate_config(config):
    """Validate required configuration."""
    required_configs = ["CLIENT_ID", "ALLOWED_DOMAIN", "EXTERNAL_IP"]
    missing = [key for key in required_configs if not config.get(key)]
    if missing:
        raise ValueError(f"Missing required configurations: {', '.join(missing)}")


def main(test_config=None, test_mode=False):
    """Run the application."""
    app = create_app(test_config)
    validate_config(app.config)
    if not test_mode:
        app.run(host="localhost", port=8081)  # pragma: no cover
    return app


if __name__ == "__main__":
    main()
