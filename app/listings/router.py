from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def listings():
    return {"message": "Listings endpoint"}