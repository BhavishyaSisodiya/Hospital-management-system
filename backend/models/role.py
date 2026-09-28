from sqlalchemy import (
    CheckConstraint,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class RoleDB(Base):
    __tablename__ = "roles"

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_roles_name_not_empty",
        ),
        Index(
            "ix_roles_name",
            "name",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    users: Mapped[list["UserDB"]] = relationship(
        "UserDB",
        back_populates="role",
    )

    employees: Mapped[list["EmployeeDB"]] = relationship(
        "EmployeeDB",
        back_populates="role",
    )