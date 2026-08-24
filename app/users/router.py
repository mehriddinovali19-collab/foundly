from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.users import service
from app.users.dependencies import get_current_user
from app.users.models import User
from app.users.schemas import Token, UserLogin, UserOut, UserRegister


router = APIRouter(
    prefix="/auth", tags=["auth"],
)

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_session),
):
    return await service.register(db, user_in)


@router.post(
    "/login",
    response_model=Token,
)
async def login_user(
    creds: UserLogin,
    db: AsyncSession = Depends(get_session),
):
    return await service.login(db, creds)



@router.get(
    "/me",
    response_model=UserOut,
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user