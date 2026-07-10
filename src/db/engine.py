from src.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from functools import lru_cache


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    db_url = settings.database_url.get_secret_value()
    engine = create_async_engine(db_url, pool_pre_ping=True)
    return engine

@lru_cache
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    async_session_maker = async_sessionmaker(bind=get_engine(), expire_on_commit=False)
    return async_session_maker

