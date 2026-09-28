from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


InvoiceStatus = Literal[
    "unpaid",
    "partially_paid",
    "paid",
    "cancelled",
]


class InvoiceBase(BaseModel):
    patient_id: int = Field(
        ...,
        gt=0,
        description="ID of the patient associated with the invoice.",
    )

    invoice_date: datetime = Field(
        ...,
        description="Date and time when the invoice was created.",
    )

    status: InvoiceStatus = Field(
        default="unpaid",
        description="Current payment status of the invoice.",
    )


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    patient_id: int | None = Field(
        default=None,
        gt=0,
        description="Updated patient ID.",
    )

    invoice_date: datetime | None = Field(
        default=None,
        description="Updated invoice date and time.",
    )

    status: InvoiceStatus | None = Field(
        default=None,
        description="Updated invoice status.",
    )


class InvoiceResponse(InvoiceBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )