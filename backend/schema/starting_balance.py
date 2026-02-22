from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StartingBalanceCreate(BaseModel):
    month: date
    cash_balance: Decimal = Field(ge=0)
    upi_balance: Decimal = Field(ge=0)

    @field_validator("month")
    @classmethod
    def validate_first_of_month(cls, v: date) -> date:
        if v.day != 1:
            raise ValueError("Month must be the first day of the month")

        if v > date.today():
            raise ValueError("Cannot create balance for future months")

        return v


class StartingBalanceResponse(BaseModel):
    id: int
    month: date
    cash_balance: Decimal
    upi_balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StartingBalanceUpdate(BaseModel):
    cash_balance: Decimal | None = Field(None, ge=0)
    upi_balance: Decimal | None = Field(None, ge=0)
