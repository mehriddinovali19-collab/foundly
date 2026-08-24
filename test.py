import asyncio

from sqlalchemy import text

from app.database import async_engine


async def test_connection():
    try:
        async with async_engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print("✅ PostgreSQL connection ishlayapti!")
            print("Result:", result.scalar())

    except Exception as e:
        print("❌ PostgreSQL connection xatosi:")
        print(e)


asyncio.run(test_connection())