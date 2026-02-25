from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import Self

from .categories import CategoryResponse


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
    transaction_date: date
    description: str = Field(..., max_length=300, min_length=1)
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod
    transaction_type: TransactionType
    category_id: int | None = Field(None)

    @model_validator(mode="after")
    def chk_expenses_category(self) -> Self:
        if self.transaction_type != TransactionType.EXPENSE or self.category_id is not None:
            return self
        raise ValueError("Category_id cannot be null for an Expense")

    @model_validator(mode="after")
    def validate_not_transfer(self) -> Self:
        if self.transaction_type == TransactionType.TRANSFER:
            raise ValueError("Use transactions/transfer for transfer transactions")
        return self

    @field_validator("transaction_date")
    @classmethod
    def validate_not_future_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Cannot create transactions for future dates")
        return v


class TransferCreate(BaseModel):
    transaction_date: date
    description: str = Field(..., max_length=300, min_length=1)
    amount: Decimal = Field(..., gt=0)
    source_method: PaymentMethod
    destination_method: PaymentMethod

    @model_validator(mode="after")
    def validate_different_methods(self) -> Self:
        if self.source_method == self.destination_method:
            raise ValueError("Cannot transfer between the same payment method")
        return self

    @field_validator("transaction_date")
    @classmethod
    def validate_not_future_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Cannot create transactions for future dates")
        return v


class TransactionResponse(BaseModel):
    id: int
    transaction_date: date
    description: str
    amount: Decimal
    payment_method: PaymentMethod
    transaction_type: TransactionType
    category_id: int | None
    linked_transfer_id: int | None
    is_debit: bool | None
    created_at: datetime
    updated_at: datetime

    category: CategoryResponse | None

    model_config = ConfigDict(from_attributes=True)


class TransactionUpdate(BaseModel):
    transaction_date: date | None = Field(None)
    description: str | None = Field(None, max_length=300, min_length=1)
    amount: Decimal | None = Field(None, gt=0)
    category_id: int | None = Field(None)

    @field_validator("transaction_date")
    @classmethod
    def validate_not_future_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Cannot create transactions for future dates")
        return v


class PaginationMetaData(BaseModel):
    next_cursor: str | None
    has_more: bool
    limit: int


class TransactionListResponse(BaseModel):
    data: List[TransactionResponse]
    pagination: PaginationMetaData
