from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.pharmacy_Stock import PharmacyStockDB
from models.pharmacy import PharmacyDB
from models.medical_batch import MedicineBatchDB

from schema.pharmacyStock import (
    PharmacyStockCreate,
    PharmacyStockUpdate,
    PharmacyStockResponse,
)

from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/pharmacy-stock",
    tags=["Pharmacy Stock"],
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


def can_manage_stock(current_user) -> bool:
    return has_role(
        current_user,
        "admin",
        "pharmacist",
    )


def can_view_stock(current_user) -> bool:
    return has_role(
        current_user,
        "admin",
        "pharmacist",
        "doctor",
        "nurse",
        "receptionist",
    )


def can_delete_stock(current_user) -> bool:
    return has_role(
        current_user,
        "admin",
    )


# ============================================================
# CREATE PHARMACY STOCK
# ============================================================

@router.post(
    "/",
    response_model=PharmacyStockResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pharmacy_stock(
    stock_data: PharmacyStockCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a stock record for a medicine batch in a pharmacy.
    """

    if not can_manage_stock(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or pharmacist can manage pharmacy stock.",
        )

    # --------------------------------------------------------
    # Check pharmacy
    # --------------------------------------------------------

    pharmacy = db.get(
        PharmacyDB,
        stock_data.pharmacy_id,
    )

    if pharmacy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pharmacy not found.",
        )

    # --------------------------------------------------------
    # Check medicine batch
    # --------------------------------------------------------

    batch = db.get(
        MedicineBatchDB,
        stock_data.batch_id,
    )

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine batch not found.",
        )

    # --------------------------------------------------------
    # Check duplicate stock
    # --------------------------------------------------------

    existing_stock = (
        db.query(PharmacyStockDB)
        .filter(
            PharmacyStockDB.pharmacy_id
            == stock_data.pharmacy_id,
            PharmacyStockDB.batch_id
            == stock_data.batch_id,
        )
        .first()
    )

    if existing_stock is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This medicine batch already exists "
                "in this pharmacy."
            ),
        )

    # --------------------------------------------------------
    # Create stock
    # --------------------------------------------------------

    stock = PharmacyStockDB(
        pharmacy_id=stock_data.pharmacy_id,
        batch_id=stock_data.batch_id,
        quantity=stock_data.quantity,
    )

    db.add(stock)

    try:
        db.commit()
        db.refresh(stock)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Pharmacy stock could not be created "
                "because of a database constraint."
            ),
        )

    return stock


# ============================================================
# GET ALL PHARMACY STOCK
# ============================================================

@router.get(
    "/",
    response_model=list[PharmacyStockResponse],
    status_code=status.HTTP_200_OK,
)
def get_pharmacy_stock(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all pharmacy stock records.
    """

    if not can_view_stock(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view pharmacy stock.",
        )

    stock_records = (
        db.query(PharmacyStockDB)
        .order_by(
            PharmacyStockDB.pharmacy_id.asc(),
            PharmacyStockDB.batch_id.asc(),
        )
        .all()
    )

    return stock_records


# ============================================================
# GET STOCK BY PHARMACY + BATCH
# ============================================================

@router.get(
    "/{pharmacy_id}/{batch_id}",
    response_model=PharmacyStockResponse,
    status_code=status.HTTP_200_OK,
)
def get_pharmacy_stock_record(
    pharmacy_id: int,
    batch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get stock for a specific pharmacy and medicine batch.
    """

    if not can_view_stock(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view pharmacy stock.",
        )

    stock = (
        db.query(PharmacyStockDB)
        .filter(
            PharmacyStockDB.pharmacy_id == pharmacy_id,
            PharmacyStockDB.batch_id == batch_id,
        )
        .first()
    )

    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pharmacy stock record not found.",
        )

    return stock


# ============================================================
# UPDATE PHARMACY STOCK
# ============================================================

@router.patch(
    "/{pharmacy_id}/{batch_id}",
    response_model=PharmacyStockResponse,
    status_code=status.HTTP_200_OK,
)
def update_pharmacy_stock(
    pharmacy_id: int,
    batch_id: int,
    stock_data: PharmacyStockUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update the quantity of an existing pharmacy stock record.
    """

    if not can_manage_stock(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or pharmacist can manage pharmacy stock.",
        )

    # --------------------------------------------------------
    # Find stock record
    # --------------------------------------------------------

    stock = (
        db.query(PharmacyStockDB)
        .filter(
            PharmacyStockDB.pharmacy_id == pharmacy_id,
            PharmacyStockDB.batch_id == batch_id,
        )
        .first()
    )

    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pharmacy stock record not found.",
        )

    # --------------------------------------------------------
    # Update quantity
    # --------------------------------------------------------

    stock.quantity = stock_data.quantity

    try:
        db.commit()
        db.refresh(stock)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pharmacy stock could not be updated.",
        )

    return stock


# ============================================================
# DELETE PHARMACY STOCK
# ============================================================

@router.delete(
    "/{pharmacy_id}/{batch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_pharmacy_stock(
    pharmacy_id: int,
    batch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a pharmacy stock record.

    Only administrators can delete stock records.
    """

    if not can_delete_stock(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete pharmacy stock.",
        )

    # --------------------------------------------------------
    # Find stock record
    # --------------------------------------------------------

    stock = (
        db.query(PharmacyStockDB)
        .filter(
            PharmacyStockDB.pharmacy_id == pharmacy_id,
            PharmacyStockDB.batch_id == batch_id,
        )
        .first()
    )

    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pharmacy stock record not found.",
        )

    # --------------------------------------------------------
    # Delete stock
    # --------------------------------------------------------

    db.delete(stock)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pharmacy stock could not be deleted.",
        )

    return None