from cloudinary.uploader import upload

import app.core.cloudinary  # noqa: F401


async def upload_image(file):
    return upload(
        file.file,
        folder="bookmyvenue/venues",
    )