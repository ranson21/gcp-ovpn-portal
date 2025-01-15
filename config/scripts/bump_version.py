import os
import toml


def main():
    # Retrieve NEW_VERSION from environment variables
    new_version = os.getenv("NEW_VERSION")
    if not new_version:
        raise ValueError("NEW_VERSION environment variable is not set")

    # Load pyproject.toml
    pyproject_path = "pyproject.toml"
    try:
        config = toml.load(pyproject_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"{pyproject_path} not found")

    # Update the version
    try:
        config["tool"]["poetry"]["version"] = new_version.lstrip("v")
    except KeyError:
        raise KeyError("Invalid pyproject.toml structure: 'tool.poetry.version' not found")

    # Write updated configuration back to pyproject.toml
    with open(pyproject_path, "w") as f:
        toml.dump(config, f)

    print(f"Version updated to {new_version} in {pyproject_path}")


if __name__ == "__main__":
    main()
