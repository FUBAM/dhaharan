from pathlib import Path

from fastapi import UploadFile

from app.core.exceptions import BadRequestException


ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def validate_image_upload(
    file: UploadFile
):
    if not file.filename:
        raise BadRequestException("No file provided")

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise BadRequestException("Unsupported file extension")

    if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise BadRequestException("Unsupported file type")

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_IMAGE_SIZE:
        raise BadRequestException(
            "File too large. Max size is 5 MB"
        )