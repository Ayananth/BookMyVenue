from fastapi import APIRouter

from app.api.routes.users import router as users_router
from app.api.routes.venues import router as venues_router


api_router = APIRouter()
api_router.include_router(users_router)
api_router.include_router(venues_router)
