from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from utils.dependencies import get_current_user

from models.invoice_item import InvoiceItemDB
from models.invoice import InvoiceDB
from models.users import UserDB

from schema.invoice_item import (
    InvoiceItemCreate,
    InvoiceItemUpdate,
    InvoiceItemResponse,
)


router = APIRouter(
    prefix="/invoice-items",
    tags=["Invoice Items"],
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_role_name(user: UserDB) -> str:
    return (
        user.role.name.lower()
        if user.role
        else ""
    )


def is_member(user: UserDB) -> bool:
    return (
        user.account_type
        and user.account_type.lower() == "member"
    )


def has_role(user: UserDB, roles: set[str]) -> bool:
    return (
        is_member(user)
        and get_role_name(user) in roles
    )


def is_admin(user: UserDB) -> bool:
    return has_role(user, {"admin"})


def can_view_invoice_items(user: UserDB) -> bool:
    return has_role(
        user,
        {
            "admin",
            "accountant",
            "receptionist",
            "pharmacist",
            "lab_technician",
        },
    )


def can_manage_invoice_items(user: UserDB) -> bool:
    return has_role(
        user,
        {
            "admin",
            "accountant",
            "receptionist",
            "pharmacist",
            "lab_technician",
        },
    )


# ============================================================
# CREATE INVOICE ITEM
# ============================================================

@router.post(
    "/",
    response_model=InvoiceItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_item(
    item_data: InvoiceItemCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_manage_invoice_items(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create invoice items.",
        )

    # --------------------------------------------------------
    # Validate invoice
    # --------------------------------------------------------

    invoice = db.get(
        InvoiceDB,
        item_data.invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    # --------------------------------------------------------
    # Validate description
    # --------------------------------------------------------

    description = item_data.description.strip()

    if not description:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Description cannot be blank.",
        )

    # --------------------------------------------------------
    # Calculate amount
    # --------------------------------------------------------

    amount = (
        Decimal(item_data.quantity)
        * item_data.unit_price
    )

    # --------------------------------------------------------
    # Create item
    # --------------------------------------------------------

    new_item = InvoiceItemDB(
        invoice_id=item_data.invoice_id,
        description=description,
        quantity=item_data.quantity,
        unit_price=item_data.unit_price,
        amount=amount,
    )

    db.add(new_item)

    try:
        db.commit()
        db.refresh(new_item)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Invoice item could not be created "
                "because of a database constraint."
            ),
        )

    return new_item


# ============================================================
# GET ALL INVOICE ITEMS
# ============================================================

@router.get(
    "/",
    response_model=list[InvoiceItemResponse],
)
def get_invoice_items(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_view_invoice_items(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view invoice items.",
        )

    return (
        db.query(InvoiceItemDB)
        .order_by(InvoiceItemDB.id.desc())
        .all()
    )

@router.get("/my/{invoice_id}", response_model=list[InvoiceItemResponse])
def get_my_invoice_items(
    invoice_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.account_type != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access this endpoint.",
        )

    if not current_user.patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    invoice = (
        db.query(InvoiceDB)
        .filter(
            InvoiceDB.id == invoice_id,
            InvoiceDB.patient_id == current_user.patient.id,
        )
        .first()
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    items = (
        db.query(InvoiceItemDB)
        .filter(InvoiceItemDB.invoice_id == invoice_id)
        .order_by(InvoiceItemDB.id)
        .all()
    )

    return items
# ============================================================
# GET ONE INVOICE ITEM
# ============================================================

@router.get(
    "/{item_id}",
    response_model=InvoiceItemResponse,
)
def get_invoice_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_view_invoice_items(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view invoice items.",
        )

    item = db.get(
        InvoiceItemDB,
        item_id,
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice item not found.",
        )

    return item


# ============================================================
# UPDATE INVOICE ITEM
# ============================================================

@router.patch(
    "/{item_id}",
    response_model=InvoiceItemResponse,
)
def update_invoice_item(
    item_id: int,
    item_data: InvoiceItemUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_manage_invoice_items(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update invoice items.",
        )

    # --------------------------------------------------------
    # Find item
    # --------------------------------------------------------

    item = db.get(
        InvoiceItemDB,
        item_id,
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice item not found.",
        )

    # --------------------------------------------------------
    # Extract supplied fields
    # --------------------------------------------------------

    update_data = item_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    # --------------------------------------------------------
    # Clean description
    # --------------------------------------------------------

    if "description" in update_data:
        description = update_data["description"].strip()

        if not description:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Description cannot be blank.",
            )

        update_data["description"] = description

    # --------------------------------------------------------
    # Calculate new amount
    # --------------------------------------------------------

    quantity = update_data.get(
        "quantity",
        item.quantity,
    )

    unit_price = update_data.get(
        "unit_price",
        item.unit_price,
    )

    if (
        "quantity" in update_data
        or "unit_price" in update_data
    ):
        update_data["amount"] = (
            Decimal(quantity) * unit_price
        )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(item, field, value)

    try:
        db.commit()
        db.refresh(item)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invoice item could not be updated.",
        )

    return item


# ============================================================
# DELETE INVOICE ITEM
# ============================================================

@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_invoice_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an administrator can delete invoice items.",
        )

    # --------------------------------------------------------
    # Find item
    # --------------------------------------------------------

    item = db.get(
        InvoiceItemDB,
        item_id,
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice item not found.",
        )

    db.delete(item)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to delete invoice item.",
        )

    return None