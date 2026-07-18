from fastapi import APIRouter

router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("/")
async def list_venues():
    return {"items": [], "message": "Venue service is ready"}
