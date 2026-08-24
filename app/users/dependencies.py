from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database import get_session
from app.users import repository
from app.users.models import User


oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


async def get_current_user(
        token: str = Depends(oauth2_schema),
        db: AsyncSession = Depends(get_session),
) -> User:

    credentials_exception=  HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id_str = payload.get("sub")


        if user_id_str is None:
            raise credentials_exception

        user_id = int(user_id_str)

    except (JWTError, ValueError):
        raise credentials_exception

    user = await repository.get_user_by_id(
        db,
        user_id, 
    )

    if user is None:
        raise credentials_exception

    return user

