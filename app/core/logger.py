import functools
import inspect
import logging
import os
import time
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 5

os.makedirs("logs", exist_ok=True)

_configured = False


def setup_logging():

    global _configured

    if _configured:
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    root.addHandler(file_handler)
    root.addHandler(console_handler)

    _configured = True


def get_logger(name: str):

    setup_logging()
    return logging.getLogger(name)


def _safe_kwargs(kwargs):

    hidden = {
        "password",
        "current_password",
        "new_password",
        "otp",
        "token",
        "refresh_token",
        "access_token",
    }

    result = {}

    for k, v in kwargs.items():

        if k.lower() in hidden:
            result[k] = "***"

        else:
            result[k] = v

    return result


def log_calls(func):

    logger = get_logger(func.__module__)

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            start = time.perf_counter()

            logger.info(
                "START %s kwargs=%s",
                func.__name__,
                _safe_kwargs(kwargs),
            )

            try:

                result = await func(*args, **kwargs)

                elapsed = time.perf_counter() - start

                logger.info(
                    "END %s %.3fs",
                    func.__name__,
                    elapsed,
                )

                return result

            except Exception:

                elapsed = time.perf_counter() - start

                logger.exception(
                    "FAILED %s after %.3fs",
                    func.__name__,
                    elapsed,
                )

                raise

        return wrapper

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        logger.info(
            "START %s kwargs=%s",
            func.__name__,
            _safe_kwargs(kwargs),
        )

        try:

            result = func(*args, **kwargs)

            elapsed = time.perf_counter() - start

            logger.info(
                "END %s %.3fs",
                func.__name__,
                elapsed,
            )

            return result

        except Exception:

            elapsed = time.perf_counter() - start

            logger.exception(
                "FAILED %s after %.3fs",
                func.__name__,
                elapsed,
            )

            raise

    return wrapper