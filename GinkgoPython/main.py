import socket
import subprocess
import sys

import uvicorn
from ginkgo.core.config import settings


def get_local_ip() -> str:
    """Get the local IP address of the machine"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "unable to determine"


def build_frontend():
    """Build the frontend using pnpm"""
    if not settings.frontend_dir.exists():
        print(
            f"Frontend directory not found at {settings.frontend_dir}. Is the submodule cloned correctly?"
        )
        sys.exit(1)

    print("Building frontend...")
    print(f"Working directory: {settings.frontend_dir}")
    try:
        result = subprocess.run(
            settings.frontend_build_command,
            cwd=settings.frontend_dir,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=True,
        )
        print("Frontend build completed successfully")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Frontend build failed: {e}")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(
            "Error: pnpm not found. Please install pnpm first (refer to: https://github.com/whatphilipcodes/GinkgoFrontend/blob/main/README.md)."
        )
        sys.exit(1)


def main():
    build_frontend()

    local_ip = get_local_ip()
    print(f"Starting server on {settings.server_host}:{settings.server_port}")
    print("Frontend URLs:")
    print(f"Local: http://localhost:{settings.server_port}")
    print(f"Network: http://{local_ip}:{settings.server_port}")

    uvicorn.run(
        "ginkgo.server:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.server_reload,
    )


if __name__ == "__main__":
    main()
