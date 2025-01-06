def test_app_debug_mode(monkeypatch):
    """Test serve command in debug mode."""
    from ovpn_portal.web.app import create_app
    from flask import Flask
    from unittest.mock import patch

    app = create_app()
    app.debug = True

    with patch.object(Flask, "run") as mock_run:
        app.run(host="localhost", port=8081)
        mock_run.assert_called_once_with(host="localhost", port=8081)


def test_create_app_with_config_object():
    """Test app creation with custom config object."""
    from ovpn_portal.web.app import create_app

    test_config = {
        "TESTING": True,
        "CLIENT_ID": "test-id",
        "ALLOWED_DOMAIN": "test.com",
    }

    app = create_app(config_object=test_config)
    assert app.config["TESTING"] is True
    assert app.config["CLIENT_ID"] == "test-id"
