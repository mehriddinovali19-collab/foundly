import asyncio

from sqlalchemy import text

from app.database import async_engine


async def main():
    async with async_engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM alembic_version")
        )

        print("✅ Eski Alembic revision tozalandi")


asyncio.run(main())