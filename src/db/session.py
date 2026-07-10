from src.db.engine import get_session_maker
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = get_session_maker()
    async with async_session() as session:
        yield session