from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.venue import ImageUploadResponse
from app.services.cloudinary_service import upload_image

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/image", response_model=ImageUploadResponse)
async def upload_venue_image(
    file: UploadFile = File(...),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed",
        )

    result = await upload_image(file)

    return ImageUploadResponse(
        public_id=result["public_id"],
        url=result["url"],
        secure_url=result["secure_url"],
        width=result["width"],
        height=result["height"],
        format=result["format"],
        bytes=result["bytes"],
    )
