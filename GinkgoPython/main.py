import socket
import subprocess
import sys

import uvicorn
from ginkgo.core.config import settings
from ginkgo.utils.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


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
        logger.error(
            f"Frontend directory not found at {settings.frontend_dir}. Is the submodule cloned correctly?"
        )
        sys.exit(1)

    logger.info("Building frontend...")
    logger.info(f"Working directory: {settings.frontend_dir}")
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
        logger.info("Frontend build completed successfully")
        if result.stdout:
            logger.debug(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Frontend build failed: {e}")
        if e.stderr:
            logger.error(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        logger.error(
            "pnpm not found. Please install pnpm first (refer to: https://github.com/whatphilipcodes/GinkgoFrontend/blob/main/README.md)."
        )
        sys.exit(1)


def main():
    build_frontend()

    local_ip = get_local_ip()
    logger.info(f"Starting server on {settings.server_host}:{settings.server_port}")
    logger.info("Frontend URLs:")
    logger.info(f"Local: http://localhost:{settings.server_port}")
    logger.info(f"Network: http://{local_ip}:{settings.server_port}")

    uvicorn.run(
        "ginkgo.server:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.server_reload,
        log_config=None,
    )


if __name__ == "__main__":
    main()
