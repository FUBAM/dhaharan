from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.modules.auth.service import get_authenticated_user
from app.modules.users.models import User


security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


bearer_scheme = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    credentials_exception = UnauthorizedException(
        "Could not validate credentials"
    )

    payload = decode_access_token(credentials.credentials)

    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")

    if not user_id:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(
            User.id == int(user_id),
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        .first()
    )

    if not user:
        raise credentials_exception

    return user


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")

    payload = decode_access_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")

    if not user_id:
        return None

    return (
        db.query(User)
        .filter(
            User.id == int(user_id),
            User.is_active == True,
            User.deleted_at.is_(None)
        )
        .first()
    )