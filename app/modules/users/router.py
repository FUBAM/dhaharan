from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.common.responses import success_response
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.schemas import (
    AccountUpdateRequest,
    ProfileUpdateRequest
)
from app.modules.users.service import (
    deactivate_account,
    get_my_profile,
    get_public_user_profile,
    update_account,
    update_profile,
    upload_profile_image
)


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)


@router.get("/me")
def my_profile_endpoint(
    current_user=Depends(get_current_user)
):
    profile = get_my_profile(current_user)

    return success_response(
        message="Profile fetched successfully",
        data=profile
    )


@router.patch("/me/profile")
def update_profile_endpoint(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    profile = update_profile(
        db=db,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Profile updated successfully",
        data=profile
    )


@router.post("/me/profile-image")
def upload_profile_image_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    profile = upload_profile_image(
        db=db,
        file=file,
        current_user=current_user
    )

    return success_response(
        message="Profile image uploaded successfully",
        data=profile
    )


@router.patch("/me/account")
def update_account_endpoint(
    payload: AccountUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    profile = update_account(
        db=db,
        payload=payload,
        current_user=current_user
    )

    return success_response(
        message="Account updated successfully",
        data=profile
    )


@router.delete("/me")
def deactivate_account_endpoint(
    current_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deactivate_account(
        db=db,
        current_password=current_password,
        current_user=current_user
    )

    return success_response(
        message="Account deactivated successfully"
    )


@router.get("/{user_id}")
def public_user_profile_endpoint(
    user_id: int,
    db: Session = Depends(get_db)
):
    profile = get_public_user_profile(
        db=db,
        user_id=user_id
    )

    return success_response(
        message="User profile fetched successfully",
        data=profile
    )