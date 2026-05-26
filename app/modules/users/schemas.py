from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.common.enums import GenderEnum

from app.common.schemas import UserSummary

class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    date_of_birth: date
    country: str = Field(..., min_length=1, max_length=100)
    province: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    gender: GenderEnum
    phone_number: str | None = Field(default=None, max_length=20)


class CurrentUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str | None
    date_of_birth: date
    country: str
    province: str
    city: str
    gender: str
    bio: str | None
    profile_image_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ProfileUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    bio: str | None = Field(default=None, max_length=2000)
    country: str | None = Field(default=None, max_length=100)
    province: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)


class AccountUpdateRequest(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, max_length=30)
    current_password: str
    new_password: str | None = Field(default=None, min_length=8)


class PublicUserProfileResponse(BaseModel):
    id: int
    name: str
    bio: str | None
    profile_image_url: str | None
    country: str | None
    province: str | None
    city: str | None
    recipe_count: int
    follower_count: int
    following_count: int


class MyProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str | None
    bio: str | None
    profile_image_url: str | None
    country: str | None
    province: str | None
    city: str | None
    is_active: bool
    created_at: datetime