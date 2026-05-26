from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.common.responses import success_response
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.schemas import LoginRequest
from app.modules.auth.service import login_user
from app.modules.users.schemas import CurrentUserResponse, UserRegisterRequest
from app.modules.users.service import create_user


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    user = create_user(db, payload)

    return success_response(
        message="User registered successfully",
        data={
            "id": user.id
        }
    )


@router.post("/login")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    result = login_user(db, payload)

    return success_response(
        message="Login successful",
        data=result
    )


@router.get("/me")
def me(
    current_user=Depends(get_current_user)
):
    user_data = CurrentUserResponse.model_validate(current_user)

    return success_response(
        message="Current user fetched successfully",
        data=user_data
    )