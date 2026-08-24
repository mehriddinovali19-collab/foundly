from collections.abc import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker


from app.core.config import settings 

url = URL.create(
    drivername="postgresql+asyncpg",
    host= settings.db_host,
    port=settings.db_port,
    username=settings.db_user,
    password=settings.db_password,
    database=settings.db_name,
)

async_engine = create_async_engine(url)
session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session 