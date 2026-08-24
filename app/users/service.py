from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.users import repository
from app.users.schemas import Token, UserLogin, UserOut, UserRegister



async def register(
        db: AsyncSession,
        user_in: UserRegister
) -> UserOut:
    existing = await repository.get_user_by_email(
        db,
        user_in.email,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists!",
        )

    if user_in.password != user_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password do not match",
        )
    hashed_pwd = hash_password(user_in.password)
    user = await repository.create_user(db, user_in, hashed_pwd,)
    return user


async def login(
        db: AsyncSession,
        creds: UserLogin,
    ) -> Token:

        user = await repository.get_user_by_email(
            db, 
            creds.email )

        if not user or not verify_password(
             creds.password,
             user.password_hash,
        ):
             raise HTTPException(
                  status_code=status.HTTP_401_UNAUTHORIZED,
                  detail="Incorrect email or password",
             )

        token = create_access_token(
             subject=str(user.id)
        )
        return Token(access_token=token)