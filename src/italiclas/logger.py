"""Logger."""

import logging
import logging.handlers
import time

import rich.logging

from italiclas.config import cfg, info

# Create a logger
logger = logging.getLogger(info.name)
logger.setLevel(logging.DEBUG)

# Add Rotating File Logger
file_handler = logging.handlers.RotatingFileHandler(
    cfg.log_file_name,
    maxBytes=cfg.max_log_file_size,
    backupCount=cfg.max_log_file_count,
)
file_formatter = logging.Formatter(
    "%(asctime)s.%(msecs)03d|%(name)s|%(levelname)s: "
    "%(message)s -- %(filename)s:%(lineno)d",
    datefmt="%Y-%m-%dT%H:%M:%SZ",  # ISO8601
)
file_formatter.converter = time.gmtime  # use UTC
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Add Console Logger
console_handler = rich.logging.RichHandler()
console_formatter = logging.Formatter(
    "%(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
console_formatter.converter = time.localtime
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
