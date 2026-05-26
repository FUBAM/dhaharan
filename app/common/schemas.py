from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationMeta


class UserSummary(BaseModel):
    id: int
    name: str
    profile_image_url: str | None = None

    model_config = {
        "from_attributes": True
    }


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


class CounterResponse(BaseModel):
    like_count: int
    comment_count: int
    bookmark_count: int


class InteractionStateResponse(BaseModel):
    is_liked: bool
    is_bookmarked: bool
    is_following_author: bool