from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, validates

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (CheckConstraint("role IN ('ADMIN', 'GUEST')", name="chk_role"),)

    @validates("username")
    def normalize_username(self, key, value):
        return value.lower() if value else value
    
    @validates("role")
    def normalize_role(self, key, value):
        return value.upper() if value else value

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(id={self.id}, username={self.username}, role={self.role})>"
        )
