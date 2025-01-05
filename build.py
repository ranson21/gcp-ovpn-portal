import subprocess
from pathlib import Path


def build():
    """Build frontend assets during package installation."""
    static_dir = Path(__file__).parent / "src" / "ovpn_portal" / "static"

    if not (static_dir / "package.json").exists():
        print("No frontend assets to build")
        return

    print("Building frontend assets...")
    try:
        # Install npm dependencies
        subprocess.run(["npm", "install"], cwd=static_dir, check=True)

        # Build frontend
        subprocess.run(["npm", "run", "build"], cwd=static_dir, check=True)

        print("Frontend build completed successfully")

    except subprocess.CalledProcessError as e:
        print(f"Frontend build failed: {e}")
        raise
    except Exception as e:
        print(f"Error during frontend build: {e}")
        raise


if __name__ == "__main__":
    build()
