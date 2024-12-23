import pytest


def test_main_function_validation():
    """Test main function config validation."""
    from ovpn_portal.run import main

    test_config = {
        "CLIENT_ID": "test-id",
        "ALLOWED_DOMAIN": "test.com",
        "EXTERNAL_IP": "1.2.3.4",
        "SECRET_KEY": "test-key",  # Add this to prevent default value
        "VPN_NETWORK": "10.0.0.0/24",  # Add this to prevent default value
    }

    # Run in test mode with test config
    app = main(test_config=test_config, test_mode=True)
    for key in test_config:
        assert app.config[key] == test_config[key], f"Config mismatch for {key}"


def test_main_function_missing_config(monkeypatch):
    """Test main function with missing config."""
    # Clear any existing environment variables
    monkeypatch.delenv("CLIENT_ID", raising=False)
    monkeypatch.delenv("ALLOWED_DOMAIN", raising=False)
    monkeypatch.delenv("EXTERNAL_IP", raising=False)

    from ovpn_portal.run import main
    import pytest

    # Provide only non-required configs
    test_config = {
        "SECRET_KEY": "test-key",
        "VPN_NETWORK": "10.0.0.0/24",
        # Explicitly set required configs to None
        "CLIENT_ID": None,
        "ALLOWED_DOMAIN": None,
        "EXTERNAL_IP": None,
    }

    with pytest.raises(ValueError) as exc_info:
        main(test_config=test_config, test_mode=True)
    assert "Missing required configurations" in str(exc_info.value)
