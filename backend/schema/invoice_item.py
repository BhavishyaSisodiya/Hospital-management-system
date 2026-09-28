from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InvoiceItemBase(BaseModel):
    invoice_id: int = Field(
        ...,
        gt=0,
        description="ID of the invoice.",
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Description of the billed item.",
    )

    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity of the item.",
    )

    unit_price: Decimal = Field(
        ...,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
        description="Price per unit.",
    )


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemUpdate(BaseModel):
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated item description.",
    )

    quantity: int | None = Field(
        default=None,
        gt=0,
        description="Updated quantity.",
    )

    unit_price: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
        description="Updated unit price.",
    )


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    amount: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )