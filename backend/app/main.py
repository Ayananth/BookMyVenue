from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.db import Base, engine
from app.admin.admin import setup_admin



@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


#Todo : change for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_admin(app, engine)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

app.include_router(api_router)

