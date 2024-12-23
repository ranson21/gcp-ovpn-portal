import tomli
from pathlib import Path


def get_version():
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomli.load(f)
    return pyproject["tool"]["poetry"]["version"]
