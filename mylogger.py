"""
Setup logging facilities
"""

import logging.config
import logging.handlers
import json
import pathlib


def filter_maker(level):
    """
    Creates logging config filter based on level
    """
    level = getattr(logging, level)

    def logging_filter(record):
        return record.levelno <= level

    return logging_filter


def setup_logging():
    """
    Configure root logger
    """
    config_file = pathlib.Path("logging_configs/config.json")
    with open(config_file, encoding="utf-8") as f:
        config = json.load(f)
    logging.config.dictConfig(config)
