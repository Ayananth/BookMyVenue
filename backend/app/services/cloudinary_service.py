import cloudinary
from cloudinary.uploader import upload

from app.core.config import settings

import app.core.cloudinary


async def upload_image(file):
    return upload(
        file.file,
        folder="bookmyvenue/venues",
    )