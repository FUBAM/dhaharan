from datetime import datetime

from pydantic import BaseModel, Field

from app.common.schemas import UserSummary


class BookmarkCreateRequest(BaseModel):
    personal_note: str | None = None


class BookmarkNoteUpdateRequest(BaseModel):
    personal_note: str | None = None


class CommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)


class CommentUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    id: int
    content: str
    author: UserSummary
    created_at: datetime
    updated_at: datetime


class BookmarkResponse(BaseModel):
    id: int
    recipe_id: int
    personal_note: str | None
    created_at: datetime


class FollowUserResponse(BaseModel):
    id: int
    name: str
    profile_image_url: str | None = None

    model_config = {
        "from_attributes": True
    }