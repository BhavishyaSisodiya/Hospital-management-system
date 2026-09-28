from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class RoleBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Role name cannot be empty.")

        return value


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Role name cannot be empty.")

        return value


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = ConfigDict(
        from_attributes=True
    )