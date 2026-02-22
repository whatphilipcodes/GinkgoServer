import io
import logging
import sys
from typing import Optional

from ginkgo.core.config import settings


class LoggerStream(io.StringIO):
    """
    Custom stream that writes output to a logger instead of stdout/stderr.
    """

    def __init__(self, logger: logging.Logger, level: int = logging.INFO):
        super().__init__()
        self.logger = logger
        self.level = level
        self.linebuf = ""

    def write(self, message: str) -> int:
        """Write message to logger, respecting the logger's configured level."""
        if message and message != "\n":
            if self.logger.isEnabledFor(self.level):
                self.logger.log(self.level, message.rstrip())
        return len(message)

    def flush(self) -> None:
        """Flush the stream."""
        pass


class NullStream(io.StringIO):
    """
    Stream that discards all output silently.
    """

    def write(self, message: str) -> int:
        """Discard message."""
        return len(message)

    def flush(self) -> None:
        """Flush the stream."""
        pass


def setup_logging() -> None:
    """
    Initialize and configure the logging system.
    If disable_library_logging is True, suppresses all library output.
    If disable_library_logging is False, redirects stdout/stderr to logger to capture all library output.
    """
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Configure uvicorn logging to use our logger
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    # If library logging is disabled, suppress all output
    if settings.disable_library_logging:
        sys.stdout = NullStream()
        sys.stderr = NullStream()
    else:
        # If library logging is enabled, redirect to logger
        logger = logging.getLogger("ginkgo.libraries")
        sys.stdout = LoggerStream(logger, logging.INFO)
        sys.stderr = LoggerStream(logger, logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for the given module name.

    Args:
        name: The module name for the logger. If None, returns the root logger.

    Returns:
        A configured logger instance.
    """
    if name is None:
        return logging.getLogger()
    return logging.getLogger(name)
