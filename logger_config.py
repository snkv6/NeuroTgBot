import asyncio
import logging
import os
import sys

from database.logs import DBLogHandler


def setup_logging() -> None:
    fmt_console = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    fmt_db = "%(message)s"

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(fmt_console))

    dbh = DBLogHandler()
    dbh.setFormatter(logging.Formatter(fmt_db))

    logging.basicConfig(level="INFO", handlers=[console, dbh], force=True)
