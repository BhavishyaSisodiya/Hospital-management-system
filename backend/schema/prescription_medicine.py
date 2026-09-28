from pydantic import BaseModel, ConfigDict, Field


class PrescriptionMedicineBase(BaseModel):
    prescription_id: int = Field(
        ...,
        gt=0,
        description="ID of the prescription.",
    )

    medicine_id: int = Field(
        ...,
        gt=0,
        description="ID of the medicine.",
    )

    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity of medicine prescribed.",
    )

    dosage: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Dosage instructions.",
    )

    duration: str | None = Field(
        default=None,
        max_length=50,
        description="Duration of medication.",
    )

    instructions: str | None = Field(
        default=None,
        max_length=255,
        description="Additional instructions.",
    )


class PrescriptionMedicineCreate(PrescriptionMedicineBase):
    pass


class PrescriptionMedicineUpdate(BaseModel):
    quantity: int | None = Field(
        default=None,
        gt=0,
        description="Updated quantity.",
    )

    dosage: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated dosage instructions.",
    )

    duration: str | None = Field(
        default=None,
        max_length=50,
        description="Updated medication duration.",
    )

    instructions: str | None = Field(
        default=None,
        max_length=255,
        description="Updated additional instructions.",
    )


class PrescriptionMedicineResponse(PrescriptionMedicineBase):
    model_config = ConfigDict(from_attributes=True)