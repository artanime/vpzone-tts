import logging
import sys
from logging.handlers import RotatingFileHandler

from core.paths import LOG_FILE, ensure_folders


def _configure():

    ensure_folders()

    logger = logging.getLogger("VPZone")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    try:

        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    except OSError:

        pass

    # Consola en UTF-8 para evitar errores con emojis en Windows.
    try:

        sys.stdout.reconfigure(encoding="utf-8")

    except (AttributeError, ValueError):

        pass

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    logger.propagate = False

    return logger


class LoggerManager:

    logger = _configure()
