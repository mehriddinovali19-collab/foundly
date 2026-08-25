from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.listings.models import Listing
from app.listings.constants import ListingStatus, ListingType
from app.listings.schemas import ListingCreate, ListingUpdate


async def get_listing_by_id(
    db: AsyncSession,
    listing_id: int,
) -> Optional[Listing]:
    result = await db.execute(
        select(Listing)
        .options(selectinload(Listing.user))
        .where(Listing.id == listing_id)
    )

    return result.scalar_one_or_none()


async def get_listings(
    db: AsyncSession,
    search: Optional[str] = None,
    listing_type: Optional[ListingType] = None,
    skip: int = 0,
    limit: int = 20,
):
    query = select(Listing).options(
        selectinload(Listing.user)
    )

    if search:
        query = query.where(
            Listing.title.ilike(f"%{search}%")
        )

    if listing_type:
        query = query.where(
            Listing.type == listing_type
        )

    count_query = select(func.count()).select_from(query.subquery())

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query
        .order_by(Listing.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    items = result.scalars().all()

    return items, total


async def get_user_listings(
    db: AsyncSession,
    user_id: int,
) -> List[Listing]:

    result = await db.execute(
        select(Listing)
        .options(selectinload(Listing.user))
        .where(Listing.user_id == user_id)
        .order_by(Listing.created_at.desc())
    )

    return result.scalars().all()


async def create_listing(
    db: AsyncSession,
    listing_in: ListingCreate,
    user_id: int,
) -> Listing:

    listing = Listing(
        title=listing_in.title,
        description=listing_in.description,
        type=listing_in.type,
        image=listing_in.image,
        date=listing_in.date,
        status=ListingStatus.ACTIVE,
        user_id=user_id,
    )

    db.add(listing)

    await db.commit()
    await db.refresh(listing)

    return listing


async def update_listing(
    db: AsyncSession,
    listing: Listing,
    update_data: ListingUpdate,
) -> Listing:

    update_dict = update_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_dict.items():
        setattr(listing, key, value)

    await db.commit()
    await db.refresh(listing)

    return listing


async def delete_listing(
    db: AsyncSession,
    listing: Listing,
) -> None:

    await db.delete(listing)
    await db.commit()


async def claim_listing(
    db: AsyncSession,
    listing: Listing,
) -> Listing:

    listing.status = ListingStatus.CLAIMED

    await db.commit()
    await db.refresh(listing)

    return listing