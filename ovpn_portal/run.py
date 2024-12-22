from ovpn_portal.app import create_app


def main():
    app = create_app()

    if not all(
        [
            app.config["CLIENT_ID"],
            app.config["ALLOWED_DOMAIN"],
            app.config["EXTERNAL_IP"],
        ]
    ):
        raise ValueError(
            "CLIENT_ID, ALLOWED_DOMAIN, and EXTERNAL_IP must be set in environment variables"
        )
    app.run(host="localhost", port=8081)


if __name__ == "__main__":
    main()
