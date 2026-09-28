from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from utils.dependencies import get_current_user

from models.medicine import MedicineDB
from models.medical_batch import MedicineBatchDB

from schema.medical_batch import (
    MedicineBatchCreate,
    MedicineBatchUpdate,
    MedicineBatchResponse,
)


router = APIRouter(
    prefix="/medicine-batches",
    tags=["Medicine Batches"],
)


# ============================================================
# ROLE HELPERS
# ============================================================

def get_role_name(user) -> str:
    """
    Safely get the user's role name.
    """
    role = getattr(user, "role", None)

    if role is None:
        return ""

    role_name = getattr(role, "name", "")

    return str(role_name).strip().lower()


def is_member(user) -> bool:
    """
    Check whether the authenticated account is a member/staff account.
    """
    account_type = getattr(user, "account_type", None)

    if account_type is None:
        return True

    return str(account_type).strip().lower() == "member"


def has_role(user, *roles: str) -> bool:
    """
    Check whether the user has one of the required roles.
    """
    if not is_member(user):
        return False

    user_role = get_role_name(user)

    allowed_roles = {
        role.strip().lower()
        for role in roles
    }

    return user_role in allowed_roles


def can_view_batches(user) -> bool:
    """
    Users allowed to view medicine batches.
    """
    return has_role(
        user,
        "admin",
        "doctor",
        "nurse",
        "pharmacist",
        "receptionist",
    )


def can_manage_batches(user) -> bool:
    """
    Users allowed to create/update medicine batches.
    """
    return has_role(
        user,
        "admin",
        "pharmacist",
    )


def can_delete_batches(user) -> bool:
    """
    Only administrators can permanently delete medicine batches.
    """
    return has_role(user, "admin")


# ============================================================
# CREATE MEDICINE BATCH
# ============================================================

@router.post(
    "/",
    response_model=MedicineBatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_medicine_batch(
    batch_data: MedicineBatchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new medicine batch.
    """

    if not can_manage_batches(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create medicine batches.",
        )

    # --------------------------------------------------------
    # Validate medicine
    # --------------------------------------------------------

    medicine = (
        db.query(MedicineDB)
        .filter(MedicineDB.id == batch_data.medicine_id)
        .first()
    )

    if medicine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found.",
        )

    # --------------------------------------------------------
    # Validate batch number
    # --------------------------------------------------------

    batch_number = batch_data.batch_number.strip()

    if not batch_number:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Batch number cannot be empty.",
        )

    # --------------------------------------------------------
    # Validate expiry date
    # --------------------------------------------------------

    if batch_data.expiry_date <= date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expiry date must be in the future.",
        )

    # --------------------------------------------------------
    # Check duplicate batch
    # --------------------------------------------------------

    existing_batch = (
        db.query(MedicineBatchDB)
        .filter(
            MedicineBatchDB.medicine_id == batch_data.medicine_id,
            MedicineBatchDB.batch_number.ilike(batch_number),
        )
        .first()
    )

    if existing_batch is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A batch with this batch number already exists for this medicine.",
        )

    # --------------------------------------------------------
    # Create batch
    # --------------------------------------------------------

    new_batch = MedicineBatchDB(
        medicine_id=batch_data.medicine_id,
        batch_number=batch_number,
        expiry_date=batch_data.expiry_date,
        unit_cost=batch_data.unit_cost,
    )

    db.add(new_batch)

    try:
        db.commit()
        db.refresh(new_batch)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medicine batch could not be created because of a database constraint.",
        )

    return new_batch


# ============================================================
# GET ALL MEDICINE BATCHES
# ============================================================

@router.get(
    "/",
    response_model=list[MedicineBatchResponse],
    status_code=status.HTTP_200_OK,
)
def get_medicine_batches(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all medicine batches.
    """

    if not can_view_batches(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view medicine batches.",
        )

    batches = (
        db.query(MedicineBatchDB)
        .order_by(MedicineBatchDB.id.asc())
        .all()
    )

    return batches


# ============================================================
# GET SINGLE MEDICINE BATCH
# ============================================================

@router.get(
    "/{batch_id}",
    response_model=MedicineBatchResponse,
    status_code=status.HTTP_200_OK,
)
def get_medicine_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get a single medicine batch by ID.
    """

    if not can_view_batches(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view medicine batches.",
        )

    batch = (
        db.query(MedicineBatchDB)
        .filter(MedicineBatchDB.id == batch_id)
        .first()
    )

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine batch not found.",
        )

    return batch


# ============================================================
# UPDATE MEDICINE BATCH
# ============================================================

@router.patch(
    "/{batch_id}",
    response_model=MedicineBatchResponse,
    status_code=status.HTTP_200_OK,
)
def update_medicine_batch(
    batch_id: int,
    batch_data: MedicineBatchUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Partially update a medicine batch.
    """

    if not can_manage_batches(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update medicine batches.",
        )

    # --------------------------------------------------------
    # Find existing batch
    # --------------------------------------------------------

    batch = (
        db.query(MedicineBatchDB)
        .filter(MedicineBatchDB.id == batch_id)
        .first()
    )

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine batch not found.",
        )

    update_data = batch_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    # --------------------------------------------------------
    # Validate batch number
    # --------------------------------------------------------

    if "batch_number" in update_data:

        batch_number = update_data["batch_number"].strip()

        if not batch_number:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Batch number cannot be empty.",
            )

        update_data["batch_number"] = batch_number

    # --------------------------------------------------------
    # Validate expiry date
    # --------------------------------------------------------

    if "expiry_date" in update_data:

        if update_data["expiry_date"] <= date.today():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Expiry date must be in the future.",
            )

    # --------------------------------------------------------
    # Determine final values
    # --------------------------------------------------------

    final_medicine_id = update_data.get(
        "medicine_id",
        batch.medicine_id,
    )

    final_batch_number = update_data.get(
        "batch_number",
        batch.batch_number,
    )

    # --------------------------------------------------------
    # Validate medicine if medicine_id is changing
    # --------------------------------------------------------

    if "medicine_id" in update_data:

        medicine = (
            db.query(MedicineDB)
            .filter(MedicineDB.id == final_medicine_id)
            .first()
        )

        if medicine is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medicine not found.",
            )

    # --------------------------------------------------------
    # Check duplicate medicine + batch combination
    # --------------------------------------------------------

    duplicate_batch = (
        db.query(MedicineBatchDB)
        .filter(
            MedicineBatchDB.medicine_id == final_medicine_id,
            MedicineBatchDB.batch_number.ilike(
                final_batch_number
            ),
            MedicineBatchDB.id != batch_id,
        )
        .first()
    )

    if duplicate_batch is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Another batch with this batch number already exists for this medicine.",
        )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(batch, field, value)

    try:
        db.commit()
        db.refresh(batch)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medicine batch could not be updated because of a database constraint.",
        )

    return batch


# ============================================================
# DELETE MEDICINE BATCH
# ============================================================

@router.delete(
    "/{batch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_medicine_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Permanently delete a medicine batch.

    Only administrators are allowed to perform this operation.
    """

    if not can_delete_batches(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete medicine batches.",
        )

    # --------------------------------------------------------
    # Find batch
    # --------------------------------------------------------

    batch = (
        db.query(MedicineBatchDB)
        .filter(MedicineBatchDB.id == batch_id)
        .first()
    )

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine batch not found.",
        )

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    db.delete(batch)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Medicine batch cannot be deleted because it is "
                "being used by existing pharmacy stock records."
            ),
        )

    return None