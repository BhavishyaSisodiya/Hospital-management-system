from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.users import UserDB
from models.role import RoleDB

from schema.users import (
    UserCreate,
    UserUpdate,
    UserResponse,
)

from utils.dependencies import require_admin
from utils.security import hash_password


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ============================================================
# CREATE USER
# ADMIN ONLY
# ============================================================

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Create a new member/staff user.

    Only an administrator can create users through this endpoint.
    """

    # --------------------------------------------------------
    # CHECK DUPLICATE EMAIL
    # --------------------------------------------------------

    existing_user = db.scalar(
        select(UserDB).where(
            UserDB.email == user_data.email
        )
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # --------------------------------------------------------
    # VERIFY ROLE
    # --------------------------------------------------------

    role = db.scalar(
        select(RoleDB).where(
            RoleDB.id == user_data.role_id
        )
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified role does not exist.",
        )

    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    user = UserDB(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),

        # Account type is controlled by the backend.
        account_type="member",

        role_id=user_data.role_id,
        is_active=True,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create user because of a database constraint.",
        )

    return user


# ============================================================
# GET USER BY ID
# ADMIN ONLY
# ============================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Get a user by ID.

    Only an administrator can access this endpoint.
    """

    user = db.scalar(
        select(UserDB).where(
            UserDB.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


# ============================================================
# UPDATE USER
# ADMIN ONLY
# ============================================================

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Partially update an existing user.

    Only fields supplied by the client are changed.
    """

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = db.scalar(
        select(UserDB).where(
            UserDB.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    # --------------------------------------------------------
    # GET ONLY SUPPLIED FIELDS
    # --------------------------------------------------------

    update_data = user_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # UPDATE NAME
    # --------------------------------------------------------

    if "name" in update_data:
        user.name = update_data["name"]

    # --------------------------------------------------------
    # UPDATE EMAIL
    # --------------------------------------------------------

    if "email" in update_data:

        existing_user = db.scalar(
            select(UserDB).where(
                UserDB.email == update_data["email"],
                UserDB.id != user_id,
            )
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another user already uses this email.",
            )

        user.email = update_data["email"]

    # --------------------------------------------------------
    # UPDATE ROLE
    # --------------------------------------------------------

    if "role_id" in update_data:

        role = db.scalar(
            select(RoleDB).where(
                RoleDB.id == update_data["role_id"]
            )
        )

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specified role does not exist.",
            )

        user.role_id = update_data["role_id"]

    # --------------------------------------------------------
    # UPDATE ACTIVE STATUS
    # --------------------------------------------------------

    if "is_active" in update_data:
        user.is_active = update_data["is_active"]

    # --------------------------------------------------------
    # UPDATE PASSWORD
    # --------------------------------------------------------

    if "password" in update_data:

        user.password_hash = hash_password(
            update_data["password"]
        )

    # --------------------------------------------------------
    # SAVE CHANGES
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update user because of a database constraint.",
        )

    return user


# ============================================================
# DELETE USER
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Permanently delete a user.

    Only an administrator can perform this operation.
    """

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = db.scalar(
        select(UserDB).where(
            UserDB.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    # --------------------------------------------------------
    # DELETE USER
    # --------------------------------------------------------

    db.delete(user)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "User cannot be deleted because "
                "other records depend on this user."
            ),
        )

    return None

