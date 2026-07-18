from fastapi import APIRouter

from app.api import venues

api_router = APIRouter()
api_router.include_router(venues.router)
