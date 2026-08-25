from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.listings import service
from app.listings.constants import ListingType
from app.listings.schemas import (
    ListingCreate,
    ListingOut,
    ListingUpdate,
    PaginatedListingsOut,
)
from app.users.dependencies import get_current_user
from app.users.models import User


router = APIRouter(
    prefix="/listings",
    tags=["listings"],
)


@router.get(
    "",
    response_model=PaginatedListingsOut,
)
async def get_listings(
    search: str | None = Query(
        None,
        description="Search listings by title",
    ),
    listing_type: ListingType | None = Query(
        None,
        alias="type",
        description="LOST or FOUND",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_all_listings(
        db=db,
        search=search,
        listing_type=listing_type,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=ListingOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_listing(
    listing_in: ListingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.create_listing(
        db,
        listing_in,
        current_user,
    )


@router.get(
    "/me",
    response_model=List[ListingOut],
)
async def get_my_listings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_user_listings(
        db,
        current_user,
    )


@router.get(
    "/{listing_id}",
    response_model=ListingOut,
)
async def get_listing_detail(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_listing_by_id(
        db,
        listing_id,
    )


@router.patch(
    "/{listing_id}",
    response_model=ListingOut,
)
async def update_listing(
    listing_id: int,
    listing_in: ListingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.update_listing(
        db,
        listing_id,
        listing_in,
        current_user,
    )


@router.delete(
    "/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await service.delete_listing(
        db,
        listing_id,
        current_user,
    )


@router.post(
    "/{listing_id}/claim",
    response_model=ListingOut,
)
async def claim_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.claim_listing(
        db,
        listing_id,
        current_user,
    )