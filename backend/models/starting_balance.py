from decimal import Decimal
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Starting_Balances(Base):
    __tablename__ = "starting_balances"

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[date] = mapped_column(Date, unique=True)
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    upi_balance: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
