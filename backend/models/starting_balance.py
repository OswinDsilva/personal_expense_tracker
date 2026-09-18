from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .user import User  # noqa: F401


class StartingBalance(Base):
    __tablename__ = "starting_balances"

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[date]
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    upi_balance: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", name="fk_user_id")
    )

    __table_args__ = (
        CheckConstraint("cash_balance >= 0 AND upi_balance >= 0", name="chk_amount_positive"),
        CheckConstraint("EXTRACT(DAY FROM month) = 1", name="chk_first_of_month"),
        UniqueConstraint("user_id","month", name="uq_month_user"),
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(month={self.month}, cash_balance={self.cash_balance}, upi_balance={self.upi_balance})>"
