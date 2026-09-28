from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.pharmacy import PharmacyDB
from models.hospital import HospitalDB

from schema.pharmacy import (
    PharmacyCreate,
    PharmacyUpdate,
    PharmacyResponse,
)

from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/pharmacies",
    tags=["Pharmacies"],
)


# ============================================================
# ROLE HELPERS
# ============================================================

def get_role_name(current_user) -> str:
    role = getattr(current_user, "role", None)

    if role is None:
        return ""

    role_name = getattr(role, "name", "")

    return str(role_name).strip().lower()


def is_member(current_user) -> bool:
    account_type = getattr(
        current_user,
        "account_type",
        None,
    )

    if account_type is None:
        return False

    return str(account_type).strip().lower() == "member"


def has_role(current_user, *roles: str) -> bool:
    if not is_member(current_user):
        return False

    current_role = get_role_name(current_user)

    allowed_roles = {
        role.strip().lower()
        for role in roles
    }

    return current_role in allowed_roles


def can_manage_pharmacy(current_user) -> bool:
    return has_role(
        current_user,
        "admin",
        "pharmacist",
    )


def can_view_pharmacy(current_user) -> bool:
    return has_role(
        current_user,
        "admin",
        "pharmacist",
        "doctor",
        "nurse",
        "receptionist",
    )


def can_delete_pharmacy(current_user) -> bool:
    return has_role(
        current_user,
        "admin",
    )


# ============================================================
# CREATE PHARMACY
# ============================================================

@router.post(
    "/",
    response_model=PharmacyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pharmacy(
    pharmacy_data: PharmacyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new pharmacy.
    """

    if not can_manage_pharmacy(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or pharmacist can create pharmacies.",
        )

    # --------------------------------------------------------
    # Clean input
    # --------------------------------------------------------

    name = pharmacy_data.name.strip()
    location = pharmacy_data.location.strip()

    if not name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pharmacy name cannot be empty.",
        )

    if not location:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pharmacy location cannot be empty.",
        )

    # --------------------------------------------------------
    # Check hospital
    # --------------------------------------------------------

    hospital = db.get(
        HospitalDB,
        pharmacy_data.hospital_id,
    )

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found.",
        )

    # --------------------------------------------------------
    # Check duplicate pharmacy
    # --------------------------------------------------------

    existing_pharmacy = (
        db.query(PharmacyDB)
        .filter(
            PharmacyDB.hospital_id == pharmacy_data.hospital_id,
            func.lower(PharmacyDB.name) == name.lower(),
        )
        .first()
    )

    if existing_pharmacy is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pharmacy with this name already exists in this hospital.",
        )

    # --------------------------------------------------------
    # Create pharmacy
    # --------------------------------------------------------

    pharmacy = PharmacyDB(
        name=name,
        location=location,
        hospital_id=pharmacy_data.hospital_id,
    )

    db.add(pharmacy)

    try:
        db.commit()
        db.refresh(pharmacy)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pharmacy could not be created because of a database constraint.",
        )

    return pharmacy


# ============================================================
# GET ALL PHARMACIES
# ============================================================

@router.get(
    "/",
    response_model=list[PharmacyResponse],
    status_code=status.HTTP_200_OK,
)
def get_pharmacies(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all pharmacies.
    """

    if not can_view_pharmacy(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view pharmacies.",
        )

    pharmacies = (
        db.query(PharmacyDB)
        .order_by(PharmacyDB.id.asc())
        .all()
    )

    return pharmacies


# ============================================================
# GET PHARMACY BY ID
# ============================================================

@router.get(
    "/{pharmacy_id}",
    response_model=PharmacyResponse,
    status_code=status.HTTP_200_OK,
)
def get_pharmacy(
    pharmacy_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get a single pharmacy by ID.
    """

    if not can_view_pharmacy(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view pharmacies.",
        )

    pharmacy = db.get(
        PharmacyDB,
        pharmacy_id,
    )

    if pharmacy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pharmacy not found.",
        )

    return pharmacy


# ============================================================
# UPDATE PHARMACY
# ============================================================

@router.patch(
    "/{pharmacy_id}",
    response_model=PharmacyResponse,
    status_code=status.HTTP_200_OK,
)
def update_pharmacy(
    pharmacy_id: int,
    pharmacy_data: PharmacyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Partially update a pharmacy.
    """

    if not can_manage_pharmacy(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or pharmacist can update pharmacies.",
        )

    # --------------------------------------------------------
    # Find pharmacy
    # --------------------------------------------------------

    pharmacy = db.get(
        PharmacyDB,
        pharmacy_id,
    )

    if pharmacy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pharmacy not found.",
        )

    # --------------------------------------------------------
    # Extract only supplied fields
    # --------------------------------------------------------

    update_data = pharmacy_data.model_dump(
        exclude_unset=True,
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    # --------------------------------------------------------
    # Clean name
    # --------------------------------------------------------

    if "name" in update_data:

        name = update_data["name"].strip()

        if not name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pharmacy name cannot be empty.",
            )

        update_data["name"] = name

    # --------------------------------------------------------
    # Clean location
    # --------------------------------------------------------

    if "location" in update_data:

        location = update_data["location"].strip()

        if not location:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pharmacy location cannot be empty.",
            )

        update_data["location"] = location

    # --------------------------------------------------------
    # Determine final values
    # --------------------------------------------------------

    final_hospital_id = update_data.get(
        "hospital_id",
        pharmacy.hospital_id,
    )

    final_name = update_data.get(
        "name",
        pharmacy.name,
    )

    # --------------------------------------------------------
    # Validate hospital if changed
    # --------------------------------------------------------

    if "hospital_id" in update_data:

        hospital = db.get(
            HospitalDB,
            final_hospital_id,
        )

        if hospital is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found.",
            )

    # --------------------------------------------------------
    # Check duplicate pharmacy
    # --------------------------------------------------------

    duplicate_pharmacy = (
        db.query(PharmacyDB)
        .filter(
            PharmacyDB.hospital_id == final_hospital_id,
            func.lower(PharmacyDB.name) == final_name.lower(),
            PharmacyDB.id != pharmacy_id,
        )
        .first()
    )

    if duplicate_pharmacy is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Another pharmacy with this name already exists in this hospital.",
        )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            pharmacy,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(pharmacy)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pharmacy could not be updated because of a database constraint.",
        )

    return pharmacy


# ============================================================
# DELETE PHARMACY
# ============================================================

@router.delete(
    "/{pharmacy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_pharmacy(
    pharmacy_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Permanently delete a pharmacy.

    Only administrators can delete pharmacies.
    """

    if not can_delete_pharmacy(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete pharmacies.",
        )

    # --------------------------------------------------------
    # Find pharmacy
    # --------------------------------------------------------

    pharmacy = db.get(
        PharmacyDB,
        pharmacy_id,
    )

    if pharmacy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pharmacy not found.",
        )

    # --------------------------------------------------------
    # Delete pharmacy
    # --------------------------------------------------------

    db.delete(pharmacy)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Pharmacy cannot be deleted because it is "
                "referenced by existing records."
            ),
        )

    return None