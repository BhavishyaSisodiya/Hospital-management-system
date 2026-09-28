from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from utils.dependencies import get_current_user

from models.invoice import InvoiceDB
from models.patient import PatientDB
from models.users import UserDB

from schema.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
)


router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
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


def can_view_invoices(user: UserDB) -> bool:
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


def can_manage_invoices(user: UserDB) -> bool:
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
# CREATE INVOICE
# ============================================================

@router.post(
    "/",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_manage_invoices(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create invoices.",
        )

    # --------------------------------------------------------
    # Validate patient
    # --------------------------------------------------------

    patient = db.get(
        PatientDB,
        invoice_data.patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # --------------------------------------------------------
    # Validate invoice date
    # --------------------------------------------------------

    invoice_date = invoice_data.invoice_date

    if invoice_date.tzinfo is None:
        invoice_date = invoice_date.replace(
            tzinfo=timezone.utc
        )

    now = datetime.now(timezone.utc)

    if invoice_date > now:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invoice date cannot be in the future.",
        )

    # --------------------------------------------------------
    # Create invoice
    # --------------------------------------------------------

    new_invoice = InvoiceDB(
        patient_id=invoice_data.patient_id,
        invoice_date=invoice_date,
        status=invoice_data.status,
    )

    db.add(new_invoice)

    try:
        db.commit()
        db.refresh(new_invoice)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invoice could not be created because of a database constraint.",
        )

    return new_invoice


# ============================================================
# GET ALL INVOICES
# ============================================================

@router.get(
    "/",
    response_model=list[InvoiceResponse],
)
def get_invoices(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_view_invoices(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view invoices.",
        )

    return (
        db.query(InvoiceDB)
        .order_by(InvoiceDB.id.desc())
        .all()
    )


# ============================================================
# GET ONE INVOICE
# ============================================================
@router.get("/my", response_model=list[InvoiceResponse])
def get_my_invoices(
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

    invoices = (
        db.query(InvoiceDB)
        .filter(
            InvoiceDB.patient_id == current_user.patient.id
        )
        .order_by(InvoiceDB.invoice_date.desc())
        .all()
    )

    return invoices

    
@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_view_invoices(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view invoices.",
        )

    invoice = db.get(
        InvoiceDB,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    return invoice


# ============================================================
# UPDATE INVOICE
# ============================================================

@router.patch(
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_manage_invoices(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update invoices.",
        )

    # --------------------------------------------------------
    # Find invoice
    # --------------------------------------------------------

    invoice = db.get(
        InvoiceDB,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    # --------------------------------------------------------
    # Extract only supplied fields
    # --------------------------------------------------------

    update_data = invoice_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    # --------------------------------------------------------
    # Validate patient if changed
    # --------------------------------------------------------

    if "patient_id" in update_data:
        patient = db.get(
            PatientDB,
            update_data["patient_id"],
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

    # --------------------------------------------------------
    # Validate invoice date if changed
    # --------------------------------------------------------

    if "invoice_date" in update_data:
        invoice_date = update_data["invoice_date"]

        if invoice_date.tzinfo is None:
            invoice_date = invoice_date.replace(
                tzinfo=timezone.utc
            )

        if invoice_date > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invoice date cannot be in the future.",
            )

        update_data["invoice_date"] = invoice_date

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(invoice, field, value)

    try:
        db.commit()
        db.refresh(invoice)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invoice could not be updated.",
        )

    return invoice


# ============================================================
# DELETE INVOICE
# ============================================================



@router.delete(
    "/{invoice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an administrator can delete invoices.",
        )

    # --------------------------------------------------------
    # Find invoice
    # --------------------------------------------------------

    invoice = db.get(
        InvoiceDB,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    db.delete(invoice)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Invoice cannot be deleted because "
                "it is referenced by existing records."
            ),
        )

    return None