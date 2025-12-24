import asyncio
import logging
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, Text

from database.base import Base, SessionLocal

logger = logging.getLogger(__name__)


class AppLog(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    ts = Column(DateTime)
    level = Column(String, nullable=False)
    name = Column(String, nullable=False)
    message = Column(Text, nullable=False)


def _level(record: logging.LogRecord) -> str:
    if record.levelno >= logging.ERROR:
        return "error"
    if record.levelno >= logging.WARNING:
        return "warning"
    return "info"


async def add_log(ts: datetime, level: str, name: str, message: str) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            session.add(AppLog(ts=ts, level=level, name=name, message=message))


class DBLogHandler(logging.Handler):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self._loop = loop

    def emit(self, record: logging.LogRecord) -> None:
        if record.name.startswith(("sqlalchemy", "asyncpg")):
            return
        try:
            if record.levelno >= logging.ERROR:
                level =  "error"
            elif record.levelno >= logging.WARNING:
                level = "warning"
            else :
                level =  "info"
            coro = add_log(datetime.fromtimestamp(record.created), level, record.name, self.format(record))
            asyncio.run_coroutine_threadsafe(coro, self._loop)

        except Exception:
            pass
