from datetime import datetime

from sqlalchemy import DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
