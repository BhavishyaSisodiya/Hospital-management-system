from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.role import RoleDB
from models.users import UserDB

from schema.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
)

from utils.dependencies import (
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


# ============================================================
# CREATE ROLE
# ============================================================

@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # --------------------------------------------------------
    # Prevent creation of the admin role
    # --------------------------------------------------------

    if role_data.name.strip().lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The admin role cannot be created through the API.",
        )

    # --------------------------------------------------------
    # Check duplicate role name
    # --------------------------------------------------------

    existing_role = db.scalar(
        select(RoleDB).where(
            RoleDB.name == role_data.name
        )
    )

    if existing_role is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role with this name already exists.",
        )

    # --------------------------------------------------------
    # Create role
    # --------------------------------------------------------

    role = RoleDB(
        name=role_data.name,
        description=role_data.description,
    )

    db.add(role)

    try:
        db.commit()
        db.refresh(role)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Role could not be created because "
                "of a database constraint."
            ),
        )

    return role


# ============================================================
# GET ALL ROLES
# ============================================================

@router.get(
    "/",
    response_model=list[RoleResponse],
    status_code=status.HTTP_200_OK,
)
def get_roles(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "pharmacist",
            "lab_technician",
            "accountant",
        )
    ),
):
    roles = db.scalars(
        select(RoleDB).order_by(
            RoleDB.id
        )
    ).all()

    return roles


# ============================================================
# GET ROLE BY ID
# ============================================================

@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "pharmacist",
            "lab_technician",
            "accountant",
        )
    ),
):
    role = db.get(
        RoleDB,
        role_id,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    return role


# ============================================================
# UPDATE ROLE
# ============================================================

@router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # --------------------------------------------------------
    # Find role
    # --------------------------------------------------------

    role = db.get(
        RoleDB,
        role_id,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    # --------------------------------------------------------
    # Get only supplied fields
    # --------------------------------------------------------

    update_data = role_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # --------------------------------------------------------
    # Check duplicate role name
    # --------------------------------------------------------

    if "name" in update_data:

        existing_role = db.scalar(
            select(RoleDB).where(
                RoleDB.name == update_data["name"],
                RoleDB.id != role_id,
            )
        )

        if existing_role is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role with this name already exists.",
            )

    # --------------------------------------------------------
    # Apply changes
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(role, field, value)

    try:
        db.commit()
        db.refresh(role)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Role could not be updated because "
                "of a database constraint."
            ),
        )

    return role


# ============================================================
# DELETE ROLE
# ============================================================

@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # --------------------------------------------------------
    # Find role
    # --------------------------------------------------------

    role = db.get(
        RoleDB,
        role_id,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    db.delete(role)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Role cannot be deleted because "
                "it is currently assigned to users "
                "or employees."
            ),
        )

    return None