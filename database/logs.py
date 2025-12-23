import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import Column, BigInteger, DateTime, String, Text

from database.base import Base, SessionLocal

logger = logging.getLogger(__name__)


class AppLog(Base):
    __tablename__ = "app_logs"

    id = Column(BigInteger, primary_key=True)
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
            asyncio.create_task(add_log(datetime.fromtimestamp(record.created), level, record.name, self.format(record)))

        except Exception:
            pass
