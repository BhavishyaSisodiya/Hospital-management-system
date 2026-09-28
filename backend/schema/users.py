from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# USER BASE
# ============================================================

class UserBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )

    email: EmailStr

    role_id: int | None = None


# ============================================================
# CREATE USER
# ============================================================

class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        max_length=128
    )


# ============================================================
# UPDATE USER
# ============================================================

class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    email: EmailStr | None = None

    role_id: int | None = None

    is_active: bool | None = None

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128
    )


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    account_type: str
    role_id: int | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )