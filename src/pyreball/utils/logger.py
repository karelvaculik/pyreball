import logging
import sys

_logger = None


def get_logger() -> logging.Logger:
    global _logger

    if _logger is not None:
        return _logger
    else:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        _logger = logging.getLogger()
        _logger.setLevel(logging.INFO)
        _logger.addHandler(handler)
        return _logger
