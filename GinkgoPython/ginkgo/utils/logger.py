import logging

from ginkgo.core.config import settings


def setup_logging() -> None:
    """
    Initialize and configure the logging system.
    """
    level = getattr(settings, "log_level", logging.INFO)

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(fmt)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    else:
        for h in root_logger.handlers:
            h.setLevel(level)
            h.setFormatter(formatter)

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)
    logging.getLogger("ginkgo.libraries").setLevel(level)

    try:
        for name, lg in logging.root.manager.loggerDict.items():
            if isinstance(lg, logging.Logger):
                lg.setLevel(level)
    except Exception:
        pass

    try:
        from transformers.utils import logging as transformers_logging

        transformers_logging.disable_progress_bar()
    except (ImportError, AttributeError):
        pass


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance for the given module name.
    """
    if name is None:
        return logging.getLogger()
    return logging.getLogger(name)
