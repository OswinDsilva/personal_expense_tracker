from datetime import date
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class BalanceMetaData(BaseModel):
    cash: Decimal = Field(default=0, ge=0)
    upi: Decimal = Field(default=0, ge=0)

    model_config = ConfigDict(from_attributes=True)


class DailyMetaData(BaseModel):
    transaction_date: date
    cash_spending: Decimal = Field(default=0, ge=0)
    upi_spending: Decimal = Field(default=0, ge=0)


class MonthlyTotals(BaseModel):
    cash_spending: Decimal = Field(default=0, ge=0)
    upi_spending: Decimal = Field(default=0, ge=0)
    cash_income: Decimal = Field(default=0, ge=0)
    upi_income: Decimal = Field(default=0, ge=0)

class MonthlyDataResponse(BaseModel):
    year: int
    month: int
    starting_balance: BalanceMetaData
    daily_breakdown: List[DailyMetaData]
    totals: MonthlyTotals
    end_balance: BalanceMetaData

    model_config = ConfigDict(from_attributes=True)
