#!/usr/bin/env python3

import enum
import sys

import pandas as pd
from loguru import logger

from dfdiskcache import DataFrameDiskCache, set_logger


class LogLevel(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    QUIET = "QUIET"


def initialize_logger(name: str, log_level: LogLevel) -> None:
    logger.remove()

    if log_level == LogLevel.QUIET:
        logger.disable(name)
        return

    if log_level == LogLevel.DEBUG:
        log_format = (
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> - <level>{message}</level>"
        )
    else:
        log_format = "<level>[{level}]</level> {message}"

    logger.add(sys.stderr, colorize=True, format=log_format, level=log_level.value)
    logger.enable(name)
    set_logger(True)


def main() -> None:
    initialize_logger(__name__, LogLevel.DEBUG)

    cache = DataFrameDiskCache()
    url = "https://raw.githubusercontent.com/pandas-dev/pandas/v2.1.3/pandas/tests/io/data/csv/iris.csv"  # noqa: E501

    df = cache.get(url)
    if df is None:
        logger.info("cache miss")
        df = pd.read_csv(url)
        cache.set(url, df)
    else:
        logger.info("cache hit")

    print(df)


if __name__ == "__main__":
    main()
