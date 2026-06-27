from fastapi import APIRouter

from app.api.routes.masters import router as masters_router
from app.api.routes.uploads import router as uploads_router
from app.api.routes.users import router as users_router
from app.api.routes.venues import router as venues_router

api_router = APIRouter()
api_router.include_router(users_router)
api_router.include_router(venues_router)
api_router.include_router(masters_router)
api_router.include_router(uploads_router)
