from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="Reviews & Ratings Service",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Reviews & Ratings Service"}
