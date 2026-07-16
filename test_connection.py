import asyncio

from sqlalchemy import text

from src.db.engine import get_engine


async def main():
    engine = get_engine()

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
