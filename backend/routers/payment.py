from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.payment import PaymentDB
from models.invoice import InvoiceDB
from schema.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
)
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


# ============================================================
# ROLE HELPERS
# ============================================================

def get_role_name(current_user):
    return (
        current_user.role.name.lower()
        if current_user.role
        else ""
    )


def is_member(current_user):
    return (
        current_user.account_type
        and current_user.account_type.lower() == "member"
    )


def has_role(current_user, *roles):
    return (
        is_member(current_user)
        and get_role_name(current_user) in roles
    )


def can_manage_payments(current_user):
    return has_role(
        current_user,
        "admin",
        "accountant",
        "receptionist",
        "pharmacist",
        "lab_technician",
    )


def can_view_payments(current_user):
    return has_role(
        current_user,
        "admin",
        "accountant",
        "receptionist",
        "pharmacist",
        "lab_technician",
    )


def is_admin(current_user):
    return has_role(
        current_user,
        "admin",
    )


def is_patient_owner(current_user, patient_id):
    return (
        current_user.account_type
        and current_user.account_type.lower() == "patient"
        and current_user.patient is not None
        and current_user.patient.id == patient_id
    )


# ============================================================
# CREATE PAYMENT
# ============================================================

@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not can_manage_payments(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, accountant, or receptionist can create payments.",
        )

    invoice = (
        db.query(InvoiceDB)
        .filter(
            InvoiceDB.id == payment_data.invoice_id
        )
        .first()
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found.",
        )

    payment_date = payment_data.payment_date

    # Normalize naive datetime to UTC.
    if payment_date.tzinfo is None:
        payment_date = payment_date.replace(
            tzinfo=timezone.utc
        )
    else:
        payment_date = payment_date.astimezone(
            timezone.utc
        )

    if payment_date > __import__("datetime").datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment date cannot be in the future.",
        )

    transaction_reference = (
        payment_data.transaction_reference.strip()
        if payment_data.transaction_reference is not None
        else None
    )

    if transaction_reference == "":
        transaction_reference = None

    payment = PaymentDB(
        invoice_id=payment_data.invoice_id,
        amount=payment_data.amount,
        payment_date=payment_date,
        payment_method=payment_data.payment_method,
        status=payment_data.status,
        transaction_reference=transaction_reference,
    )

    db.add(payment)

    try:
        db.commit()
        db.refresh(payment)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment could not be created. Transaction reference may already exist.",
        )

    return payment


# ============================================================
# GET ALL PAYMENTS
# ============================================================

@router.get(
    "/",
    response_model=list[PaymentResponse],
)
def get_payments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if can_view_payments(current_user):
        return (
            db.query(PaymentDB)
            .order_by(PaymentDB.id.desc())
            .all()
        )

    # Patient can see only payments belonging to
    # their own invoices.
    if (
        current_user.account_type
        and current_user.account_type.lower() == "patient"
        and current_user.patient is not None
    ):
        return (
            db.query(PaymentDB)
            .join(
                InvoiceDB,
                PaymentDB.invoice_id == InvoiceDB.id,
            )
            .filter(
                InvoiceDB.patient_id
                == current_user.patient.id
            )
            .order_by(PaymentDB.id.desc())
            .all()
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to view payments.",
    )


# ============================================================
# GET PAYMENT BY ID
# ============================================================

@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    payment = (
        db.query(PaymentDB)
        .filter(
            PaymentDB.id == payment_id
        )
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found.",
        )

    invoice = db.get(
        InvoiceDB,
        payment.invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated invoice not found.",
        )

    if can_view_payments(current_user):
        return payment

    if is_patient_owner(
        current_user,
        invoice.patient_id,
    ):
        return payment

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to view this payment.",
    )


# ============================================================
# UPDATE PAYMENT
# ============================================================

@router.patch(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not can_manage_payments(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, accountant, or receptionist can update payments.",
        )

    payment = (
        db.query(PaymentDB)
        .filter(
            PaymentDB.id == payment_id
        )
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found.",
        )

    update_data = payment_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    # --------------------------------------------------------
    # Normalize payment date
    # --------------------------------------------------------

    if "payment_date" in update_data:
        payment_date = update_data["payment_date"]

        if payment_date.tzinfo is None:
            payment_date = payment_date.replace(
                tzinfo=timezone.utc
            )
        else:
            payment_date = payment_date.astimezone(
                timezone.utc
            )

        if payment_date > __import__("datetime").datetime.now(
            timezone.utc
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment date cannot be in the future.",
            )

        update_data["payment_date"] = payment_date

    # --------------------------------------------------------
    # Normalize transaction reference
    # --------------------------------------------------------

    if "transaction_reference" in update_data:
        transaction_reference = (
            update_data["transaction_reference"]
        )

        if transaction_reference is not None:
            transaction_reference = (
                transaction_reference.strip()
            )

            if transaction_reference == "":
                transaction_reference = None

        update_data["transaction_reference"] = (
            transaction_reference
        )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            payment,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(payment)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment could not be updated. Transaction reference may already exist.",
        )

    return payment


# ============================================================
# DELETE PAYMENT
# ============================================================

@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete payments.",
        )

    payment = (
        db.query(PaymentDB)
        .filter(
            PaymentDB.id == payment_id
        )
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found.",
        )

    db.delete(payment)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment could not be deleted.",
        )

    return None