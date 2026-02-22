from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CASH = "CASH"


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"
    ADJUSTMENT_CREDIT = "ADJUSTMENT_CREDIT"
    ADJUSTMENT_DEBIT = "ADJUSTMENT_DEBIT"


class TransactionCreate(BaseModel):
    id: int
    transaction_date: date
    description: str = Field(..., max_length=300, min_length=8)
    amount: Decimal = Field(..., ge=0)
    payment_method: PaymentMethod
    transaction_type: TransactionType
    """
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", name="fk_category_id")
    )
    linked_transfer_id: Mapped[int | None] = mapped_column(
        ForeignKey("transactions.id", name="fk_linked_transaction_id")
    )
    """
    is_debit: bool | None = Field(None)
    created_at: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)
    """
    category: Mapped["Category"] = relationship()
    """
    '''
    __table_args__ = (
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
    '''

    @model_validator("after")
    def chk_expenses_category(self) -> Self:
        if self.transaction_type != "EXPENSE" or self.category_id is not None:
            return self
        raise ValueError("Category_id cannot be null for an Expense")

    @model_validator("after")
    def chk_non_transfer_debit(self) -> Self:
        if self.transaction_type == "TRANSFER" or self.is_debit is None:
            return self
        raise ValueError("is_debit has to be null for a Non-Transfer")

    @model_validator("after")
    def chk_transfer_debit(self) -> Self:
        if self.transaction_type != "TRANSFER" or self.is_debit is not None:
            return self
        raise ValueError("is_debit cannot be null for a Transfer")

    @model_validator("after")
    def chk_transfer_link(self) -> Self:
        if self.transaction_type == "TRANSFER" or self.linked_transfer_id is not None:
            return self
        raise ValueError("No linked id for non-transfers")


class TransactionResponse(BaseModel):
    id: int
    transaction_date: date
    description: str = Field(..., max_length=300, min_length=8)
    amount: Decimal = Field(..., ge=0)
    payment_method: PaymentMethod
    transaction_type: TransactionType
    category_id: int | None
    linked_transfer_id: int | None
    is_debit: bool | None
    created_at: datetime
    updated_at: datetime


class TransactionUpdate(BaseModel):
    pass


"""
class TransferTransactionCreate(BaseModel):
    pass
"""
