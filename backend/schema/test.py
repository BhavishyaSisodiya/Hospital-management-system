from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class TestTypeBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    price: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Test type name cannot be empty.")

        return value


class TestTypeCreate(TestTypeBase):
    pass


class TestTypeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2,
    )

    model_config = ConfigDict(
        extra="forbid",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Test type name cannot be empty.")

        return value


class TestTypeResponse(TestTypeBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )