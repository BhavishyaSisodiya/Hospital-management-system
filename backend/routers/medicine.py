from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.medicine import MedicineDB
from schema.medicine import (
    MedicineCreate,
    MedicineUpdate,
    MedicineResponse,
)
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/medicines",
    tags=["Medicines"],
)


# ============================================================
# ROLE HELPERS
# ============================================================

def get_role_name(current_user) -> str:
    """
    Safely return the current user's role name.
    """
    if not current_user:
        return ""

    role = getattr(current_user, "role", None)

    if not role:
        return ""

    role_name = getattr(role, "name", None)

    if not role_name:
        return ""

    return role_name.strip().lower()


def is_member(current_user) -> bool:
    """
    Check whether the authenticated account is a member account.
    """
    account_type = getattr(current_user, "account_type", None)

    if not account_type:
        return False

    return account_type.strip().lower() == "member"


def is_admin_or_pharmacist(current_user) -> bool:
    """
    Admin and pharmacist can create, update and delete medicines.
    """
    return (
        is_member(current_user)
        and get_role_name(current_user) in {
            "admin",
            "pharmacist",
        }
    )


def is_staff_viewer(current_user) -> bool:
    """
    Staff members who are allowed to view medicines.
    """
    return (
        is_member(current_user)
        and get_role_name(current_user) in {
            "admin",
            "pharmacist",
            "doctor",
            "nurse",
            "receptionist",
        }
    )


# ============================================================
# CREATE MEDICINE
# ============================================================

@router.post(
    "/",
    response_model=MedicineResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_medicine(
    medicine_data: MedicineCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not is_admin_or_pharmacist(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or pharmacist can create medicines.",
        )

    # --------------------------------------------------------
    # Normalize input
    # --------------------------------------------------------

    medicine_name = medicine_data.name.strip()

    manufacturer = (
        medicine_data.manufacturer.strip()
        if medicine_data.manufacturer
        else None
    )

    # --------------------------------------------------------
    # Case-insensitive duplicate check
    # --------------------------------------------------------

    existing_medicine = (
        db.query(MedicineDB)
        .filter(
            MedicineDB.name.ilike(medicine_name)
        )
        .first()
    )

    if existing_medicine:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medicine with this name already exists.",
        )

    # --------------------------------------------------------
    # Create medicine
    # --------------------------------------------------------

    medicine = MedicineDB(
        name=medicine_name,
        manufacturer=manufacturer,
        unit_price=medicine_data.unit_price,
    )

    db.add(medicine)

    try:
        db.commit()
        db.refresh(medicine)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medicine with this name already exists or violates a database constraint.",
        )

    return medicine


# ============================================================
# GET ALL MEDICINES
# ============================================================

@router.get(
    "/",
    response_model=list[MedicineResponse],
)
def get_medicines(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not is_staff_viewer(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view medicines.",
        )

    medicines = (
        db.query(MedicineDB)
        .order_by(MedicineDB.id)
        .all()
    )

    return medicines


# ============================================================
# GET MEDICINE BY ID
# ============================================================

@router.get(
    "/{medicine_id}",
    response_model=MedicineResponse,
)
def get_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not is_staff_viewer(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view medicines.",
        )

    medicine = (
        db.query(MedicineDB)
        .filter(MedicineDB.id == medicine_id)
        .first()
    )

    if medicine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found.",
        )

    return medicine


# ============================================================
# UPDATE MEDICINE
# ============================================================

@router.put(
    "/{medicine_id}",
    response_model=MedicineResponse,
)
def update_medicine(
    medicine_id: int,
    medicine_data: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not is_admin_or_pharmacist(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or pharmacist can update medicines.",
        )

    # --------------------------------------------------------
    # Find medicine
    # --------------------------------------------------------

    medicine = (
        db.query(MedicineDB)
        .filter(MedicineDB.id == medicine_id)
        .first()
    )

    if medicine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found.",
        )

    # --------------------------------------------------------
    # Get only fields supplied by client
    # --------------------------------------------------------

    update_data = medicine_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # Normalize string values
    # --------------------------------------------------------

    if "name" in update_data:
        update_data["name"] = update_data["name"].strip()

        if not update_data["name"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Medicine name cannot be empty.",
            )

    if "manufacturer" in update_data:
        if update_data["manufacturer"] is not None:
            update_data["manufacturer"] = (
                update_data["manufacturer"].strip()
            )

            if not update_data["manufacturer"]:
                update_data["manufacturer"] = None

    # --------------------------------------------------------
    # Check duplicate name
    # --------------------------------------------------------

    if "name" in update_data:

        existing_medicine = (
            db.query(MedicineDB)
            .filter(
                MedicineDB.name.ilike(update_data["name"]),
                MedicineDB.id != medicine_id,
            )
            .first()
        )

        if existing_medicine:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another medicine with this name already exists.",
            )

    # --------------------------------------------------------
    # Apply updates
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(medicine, field, value)

    try:
        db.commit()
        db.refresh(medicine)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medicine could not be updated because it violates a database constraint.",
        )

    return medicine


# ============================================================
# DELETE MEDICINE
# ============================================================

@router.delete(
    "/{medicine_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not is_admin_or_pharmacist(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or pharmacist can delete medicines.",
        )

    # --------------------------------------------------------
    # Find medicine
    # --------------------------------------------------------

    medicine = (
        db.query(MedicineDB)
        .filter(MedicineDB.id == medicine_id)
        .first()
    )

    if medicine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found.",
        )

    # --------------------------------------------------------
    # Delete
    #
    # If this medicine is referenced by batches or
    # prescription items, the database FK constraint should
    # prevent deletion.
    # --------------------------------------------------------

    db.delete(medicine)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Medicine cannot be deleted because it is "
                "referenced by existing batches, prescriptions, "
                "or other records."
            ),
        )

    # HTTP 204 must not return a response body
    return None

