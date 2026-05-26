from app.modules.users.schemas import UserRegisterRequest
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.common.upload import validate_image_upload
from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException
)
from app.modules.recipes.models import Recipe
from app.modules.social.models import (
    Bookmark,
    Comment,
    Follow,
    RecipeLike
)
from app.modules.users.models import User
from app.modules.users.schemas import (
    AccountUpdateRequest,
    MyProfileResponse,
    ProfileUpdateRequest,
    PublicUserProfileResponse
)
from app.core.security import (
    hash_password,
    verify_password
)


def get_active_user_by_id(
    db: Session,
    user_id: int
) -> User | None:
    return (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        .first()
    )

def get_user_by_email(
    db: Session,
    email: str
):
    return (
        db.query(User)
        .filter(
            User.email == email,
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        .first()
    )

def create_user(
    db: Session,
    payload: UserRegisterRequest
):
    existing = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if existing:
        raise BadRequestException("Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        date_of_birth=payload.date_of_birth,
        country=payload.country,
        province=payload.province,
        city=payload.city,
        gender=payload.gender,
        phone_number=payload.phone_number,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def get_my_profile(
    current_user: User
):
    return MyProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        bio=current_user.bio,
        profile_image_url=current_user.profile_image_url,
        country=current_user.country,
        province=current_user.province,
        city=current_user.city,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


def update_profile(
    db: Session,
    payload: ProfileUpdateRequest,
    current_user: User
):
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return get_my_profile(current_user)


def upload_profile_image(
    db: Session,
    file: UploadFile,
    current_user: User
):
    validate_image_upload(file)

    extension = Path(file.filename).suffix.lower()

    filename = f"{uuid4()}{extension}"
    save_path = Path("app/uploads/profiles") / filename

    with open(save_path, "wb") as buffer:
        buffer.write(file.file.read())

    current_user.profile_image_url = (
        f"{settings.BASE_URL}/uploads/profiles/{filename}"
    )

    db.commit()
    db.refresh(current_user)

    return get_my_profile(current_user)


def update_account(
    db: Session,
    payload: AccountUpdateRequest,
    current_user: User
):
    if not verify_password(
        payload.current_password,
        current_user.password_hash
    ):
        raise ForbiddenException("Current password is incorrect")

    if payload.email:
        existing = (
            db.query(User)
            .filter(
                User.email == payload.email,
                User.id != current_user.id
            )
            .first()
        )

        if existing:
            raise BadRequestException("Email already in use")

        current_user.email = payload.email

    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number

    if payload.new_password:
        current_user.password_hash = hash_password(
            payload.new_password
        )

    db.commit()
    db.refresh(current_user)

    return get_my_profile(current_user)


def get_public_user_profile(
    db: Session,
    user_id: int
):
    user = get_active_user_by_id(db, user_id)

    if not user:
        raise NotFoundException("User not found")

    recipe_count = (
        db.query(Recipe)
        .filter(
            Recipe.user_id == user.id,
            Recipe.visibility == "public",
            Recipe.deleted_at.is_(None)
        )
        .count()
    )

    follower_count = (
        db.query(Follow)
        .filter(Follow.following_id == user.id)
        .count()
    )

    following_count = (
        db.query(Follow)
        .filter(Follow.follower_id == user.id)
        .count()
    )

    return PublicUserProfileResponse(
        id=user.id,
        name=user.name,
        bio=user.bio,
        profile_image_url=user.profile_image_url,
        country=user.country,
        province=user.province,
        city=user.city,
        recipe_count=recipe_count,
        follower_count=follower_count,
        following_count=following_count
    )


def deactivate_account(
    db: Session,
    current_user: User,
    current_password: str
):
    if not verify_password(
        current_password,
        current_user.password_hash
    ):
        raise UnauthorizedException(
            "Current password is incorrect"
        )

    db.query(RecipeLike).filter(
        RecipeLike.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.query(Comment).filter(
        Comment.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.query(Follow).filter(
        Follow.follower_id == current_user.id
    ).delete(synchronize_session=False)

    db.query(Follow).filter(
        Follow.following_id == current_user.id
    ).delete(synchronize_session=False)

    db.query(Recipe).filter(
        Recipe.user_id == current_user.id
    ).update(
        {
            "deleted_at": datetime.utcnow()
        },
        synchronize_session=False
    )

    current_user.is_active = False
    current_user.deleted_at = datetime.utcnow()

    db.commit()