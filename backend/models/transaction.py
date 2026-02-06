from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .category import Category


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(300))
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    payment_method: Mapped[str] = mapped_column(String(4))
    transaction_type: Mapped[str] = mapped_column(String(20))
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", name="fk_category_id")
    )
    linked_transfer_id: Mapped[int | None] = mapped_column(
        ForeignKey("transactions.id", name="fk_linked_transaction_id")
    )
    is_debit: Mapped[bool | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category: Mapped["Category"] = relationship()

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_amount_positive"),
        CheckConstraint(
            "transaction_type <> 'EXPENSE' OR category_id IS NOT NULL",
            name="chk_expenses_category",
        ),
        CheckConstraint(
            "transaction_type = 'TRANSFER' OR is_debit IS NULL",
            name="chk_non_transfer_debit",
        ),
        CheckConstraint("payment_method IN ('UPI','CASH')", name="chk_payment_method"),
        CheckConstraint(
            """
            transaction_type IN (
            'INCOME',
            'EXPENSE',
            'TRANSFER',
            'ADJUSTMENT_CREDIT',
            'ADJUSTMENT_DEBIT'
            )
            """,
            name="chk_transaction_type",
        ),
        CheckConstraint(
            "transaction_type <> 'TRANSFER' OR is_debit IS NOT NULL",
            name="chk_transfer_debit",
        ),
        CheckConstraint(
            "transaction_type = 'TRANSFER' OR linked_transfer_id IS NULL",
            name="chk_transfer_link",
        ),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, date={self.transaction_date}, amount={self.amount}, type={self.transaction_type})>"
