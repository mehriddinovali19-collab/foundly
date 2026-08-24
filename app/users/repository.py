from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.users.schemas import UserRegister

async def get_user_by_id(
        db: AsyncSession,
        user_id: int,
) -> Optional[User]:
    result = await db.execute(select(User).where(User.id ==user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(
        db: AsyncSession,
        email: str
) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()



async def create_user(
        db: AsyncSession,
        user_in: UserRegister,
        hashed_password: str,    
) -> User:
    user = User(
        email = user_in.email,
        password_hash= hashed_password,)
    
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user
