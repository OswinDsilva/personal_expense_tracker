from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    func,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    payment_method: Mapped[str] = mapped_column(String(4))
    transaction_type: Mapped[str] = mapped_column(String(20))
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("category.id", name="fk_category_id")
    )
    linked_transfer_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("transactions.id", name="fk_linked_transaction_id")
    )
    is_debit: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

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
        CheckConstraint(payment_method.in_(["UPI", "CASH"]), name="chk_payment_method"),
        CheckConstraint(
            transaction_type.in_(
                [
                    "EXPENSE",
                    "INCOME",
                    "TRANSFER",
                    "ADJUSTMENT_CREDIT",
                    "ADJUSTMENT_DEBIT",
                ],
                name="chk_transaction_type",
            )
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
