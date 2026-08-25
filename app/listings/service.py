from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.listings import repository
from app.listings.constants import ListingStatus, ListingType
from app.listings.schemas import (
    ListingCreate,
    ListingUpdate,
    PaginatedListingsOut,
)
from app.users.models import User


async def get_all_listings(
    db: AsyncSession,
    search: str | None = None,
    listing_type: ListingType | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedListingsOut:

    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)

    skip = (page - 1) * page_size

    items, total = await repository.get_listings(
        db=db,
        search=search,
        listing_type=listing_type,
        skip=skip,
        limit=page_size,
    )

    return PaginatedListingsOut(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


async def get_listing_by_id(
    db: AsyncSession,
    listing_id: int,
):
    listing = await repository.get_listing_by_id(
        db,
        listing_id,
    )

    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    return listing


async def create_listing(
    db: AsyncSession,
    listing_in: ListingCreate,
    current_user: User,
):

    return await repository.create_listing(
        db,
        listing_in,
        current_user.id,
    )


async def update_listing(
    db: AsyncSession,
    listing_id: int,
    update_data: ListingUpdate,
    current_user: User,
):

    listing = await get_listing_by_id(
        db,
        listing_id,
    )

    if listing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this listing",
        )

    return await repository.update_listing(
        db,
        listing,
        update_data,
    )


async def delete_listing(
    db: AsyncSession,
    listing_id: int,
    current_user: User,
) -> None:

    listing = await get_listing_by_id(
        db,
        listing_id,
    )

    if listing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this listing",
        )

    await repository.delete_listing(
        db,
        listing,
    )


async def claim_listing(
    db: AsyncSession,
    listing_id: int,
    current_user: User,
):

    listing = await get_listing_by_id(
        db,
        listing_id,
    )

    if listing.status == ListingStatus.CLAIMED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This listing has already been claimed",
        )

    return await repository.claim_listing(
        db,
        listing,
    )


async def get_user_listings(
    db: AsyncSession,
    current_user: User,
):

    return await repository.get_user_listings(
        db,
        current_user.id,
    )