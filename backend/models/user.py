from datetime import datetime

from argon2 import PasswordHasher
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

    _pwd_hasher = PasswordHasher()

    __table_args__ = (CheckConstraint("role IN ('ADMIN', 'GUEST')", name="chk_role"),)

    @validates("username")
    def normalize_username(self, key, value):
        return value.lower() if value else value
    
    @validates("role")
    def normalize_role(self, key, value):
        return value.upper() if value else value
    
    @property
    def password(self):
        raise AttributeError("Password is write-only")
    
    @password.setter
    def password(self, plain_password:str):
        self.password_hash = self._pwd_hasher.hash(plain_password)

    def verify_password(self,plain_password):
        return self._pwd_hasher.verify(self.password_hash,plain_password)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(id={self.id}, username={self.username}, role={self.role})>"
        )
