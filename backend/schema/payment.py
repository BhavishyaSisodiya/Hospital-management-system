from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PaymentMethod = Literal[
    "cash",
    "card",
    "upi",
    "bank_transfer",
    "other",
]

PaymentStatus = Literal[
    "pending",
    "completed",
    "failed",
    "refunded",
]


class PaymentBase(BaseModel):
    invoice_id: int = Field(
        ...,
        gt=0,
        description="ID of the invoice for this payment.",
    )

    amount: Decimal = Field(
        ...,
        gt=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
        description="Payment amount.",
    )

    payment_date: datetime = Field(
        ...,
        description="Date and time when the payment was made.",
    )

    payment_method: PaymentMethod = Field(
        ...,
        description="Payment method.",
    )

    status: PaymentStatus = Field(
        default="completed",
        description="Payment status.",
    )

    transaction_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Unique transaction reference, if available.",
    )


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Decimal | None = Field(
        default=None,
        gt=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )

    payment_date: datetime | None = None

    payment_method: PaymentMethod | None = None

    status: PaymentStatus | None = None

    transaction_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class PaymentResponse(PaymentBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )