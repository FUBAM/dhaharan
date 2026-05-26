from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, verify_password
from app.modules.auth.schemas import LoginRequest, LoginResponseData
from app.modules.users.models import User
from app.modules.users.service import get_user_by_email


def login_user(
    db: Session,
    payload: LoginRequest
) -> LoginResponseData:
    user = get_user_by_email(db, payload.email)

    if not user:
        raise UnauthorizedException("Invalid email or password")

    if not verify_password(payload.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")

    token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    return LoginResponseData(
        access_token=token,
        token_type="bearer"
    )


def get_authenticated_user(
    db: Session,
    user_id: int
) -> User:
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        .first()
    )

    if not user:
        raise UnauthorizedException("Invalid authentication")

    return user