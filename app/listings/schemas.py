from datetime import date, datetime
from typing import List, Optional
from pydantic import Field, BaseModel
from app.listings.constants import ListingStatus, ListingType
from app.users.schemas import UserOut


class ListingCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    description: str = Field(max_length=300)
    type: ListingType
    image: Optional[str] = None
    date: date


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    type: Optional[ListingType] = None
    image: Optional[str] = None
    date: Optional[date] = None


class ListingOut(BaseModel):
    id: int
    title: str
    description: str
    type: ListingType
    image: Optional[str] = None
    date: date
    status: ListingStatus
    created_at: datetime
    user_id: int
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True

class PaginatedListingsOut(BaseModel):
    items: List[ListingOut]
    total: int
    page: int
    page_size: int