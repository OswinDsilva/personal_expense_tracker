from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, validates

from ..database import Base
from .user import User  # noqa: F401


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="fk_user_id")
    )

    __table_args__ = (
        UniqueConstraint("user_id","name", name="uq_name_user"),
    )

    @validates("name")
    def normalize_name(self, key, value):
        return value.lower() if value else value

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name})>"
