from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class UserDB(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_users_name_not_empty",
        ),
        Index(
            "ix_users_role_id",
            "role_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    account_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    
    role_id:Mapped[int]= mapped_column(
        ForeignKey(
            "roles.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    role: Mapped["RoleDB"] = relationship(
        "RoleDB",
        back_populates="users",
    )

    patient: Mapped["PatientDB | None"] = relationship(
        "PatientDB",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )