from pydantic import BaseModel, ConfigDict, Field, EmailStr


class HospitalBase(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=150
    )

    address: str = Field(
        min_length=1,
        max_length=255
    )

    phone: str = Field(
        min_length=1,
        max_length=20
    )

    email: EmailStr


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    address: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    phone: str | None = Field(
        default=None,
        min_length=1,
        max_length=20
    )

    email: EmailStr | None = None


class HospitalResponse(HospitalBase):

    id: int

    model_config = ConfigDict(
        from_attributes=True
    )