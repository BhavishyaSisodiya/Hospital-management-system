from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from database import get_db
from models.users import UserDB
from utils.jwt import decode_access_token


# ============================================================
# HTTP BEARER SCHEME
# ============================================================

bearer_scheme = HTTPBearer(
    auto_error=False
)


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> UserDB:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    # --------------------------------------------------------
    # Check Authorization header
    # --------------------------------------------------------

    if credentials is None:
        raise credentials_exception

    token = credentials.credentials

    # --------------------------------------------------------
    # Decode JWT
    # --------------------------------------------------------

    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    # --------------------------------------------------------
    # Get user ID
    # --------------------------------------------------------

    user_id = payload.get("sub")

    if user_id is None:
        raise credentials_exception

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        raise credentials_exception

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = (
        db.query(UserDB)
        .filter(UserDB.id == user_id)
        .first()
    )

    if user is None:
        raise credentials_exception

    # --------------------------------------------------------
    # Check active account
    # --------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return user


# ============================================================
# REQUIRE PATIENT
# ============================================================

def require_patient(
    current_user: UserDB = Depends(get_current_user),
) -> UserDB:

    account_type = (
        current_user.account_type.lower()
        if current_user.account_type
        else ""
    )

    if account_type != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required.",
        )

    return current_user


# ============================================================
# REQUIRE MEMBER
# ============================================================

def require_member(
    current_user: UserDB = Depends(get_current_user),
) -> UserDB:

    account_type = (
        current_user.account_type.lower()
        if current_user.account_type
        else ""
    )

    if account_type != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Member access required.",
        )

    return current_user


# ============================================================
# REQUIRE ADMIN
# ============================================================

def require_admin(
    current_user: UserDB = Depends(get_current_user),
) -> UserDB:

    account_type = (
        current_user.account_type.lower()
        if current_user.account_type
        else ""
    )

    if account_type != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    if current_user.role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    role_name = current_user.role.name.lower()

    if role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user


# ============================================================
# ROLE-BASED AUTHORIZATION
# ============================================================

def require_role(
    *allowed_roles: str,
) -> Callable:

    def role_checker(
        current_user: UserDB = Depends(
            get_current_user
        ),
    ) -> UserDB:

        account_type = (
            current_user.account_type.lower()
            if current_user.account_type
            else ""
        )

        # ----------------------------------------------------
        # Must be a member
        # ----------------------------------------------------

        if account_type != "member":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Member access required.",
            )

        # ----------------------------------------------------
        # Must have a role
        # ----------------------------------------------------

        if current_user.role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have an assigned role.",
            )

        # ----------------------------------------------------
        # Check role
        # ----------------------------------------------------

        role_name = current_user.role.name.lower()

        allowed = {
            role.lower()
            for role in allowed_roles
        }

        if role_name not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

        return current_user

    return role_checker