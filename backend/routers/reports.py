from calendar import monthrange
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, extract, select
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..models import StartingBalance, Transaction, User
from ..schema import MonthlyDataResponse
from ..utils.reports import is_credit, is_debit

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/data/{year}/{month}", response_model=MonthlyDataResponse)
def get_monthly_data(
    year: int,
    month: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    starting_balance = db.execute(
        select(StartingBalance).where(StartingBalance.month == date(year, month, 1))
    ).scalar_one_or_none()

    if not starting_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Starting balance not found for the month"
        )

    transactions = (
        db.execute(
            select(Transaction)
            .where(
                and_(
                    extract("year", Transaction.transaction_date) == year,
                    extract("month", Transaction.transaction_date) == month,
                )
            )
            .order_by(Transaction.transaction_date, Transaction.id)
        )
        .scalars()
        .all()
    )

    cash_spending = sum(
        t.amount for t in transactions if t.payment_method == "CASH" and is_debit(t)
    )
    upi_spending = sum(t.amount for t in transactions if t.payment_method == "UPI" and is_debit(t))
    cash_income = sum(t.amount for t in transactions if t.payment_method == "CASH" and is_credit(t))
    upi_income = sum(t.amount for t in transactions if t.payment_method == "UPI" and is_credit(t))

    totals = {
        "cash_spending": cash_spending,
        "upi_spending": upi_spending,
        "cash_income": cash_income,
        "upi_income": upi_income,
    }

    date_range = monthrange(year, month)[1]

    daily_data = {}

    for day in range(1, date_range + 1):
        daily_data[day] = {
            "transaction_date": date(year, month, day),
            "cash_spending": 0,
            "upi_spending": 0,
        }

    for t in transactions:
        if is_debit(t):
            if t.payment_method == "CASH":
                daily_data[t.transaction_date.day]["cash_spending"] += t.amount
            else:
                daily_data[t.transaction_date.day]["upi_spending"] += t.amount

    ending_cash_balance = starting_balance.cash_balance - cash_spending + cash_income
    ending_upi_balance = starting_balance.upi_balance - upi_spending + upi_income
    ending_balances = {"cash": ending_cash_balance, "upi": ending_upi_balance}

    required_data = {
        "year": year,
        "month": month,
    }

    required_data["starting_balance"] = {
        "cash": starting_balance.cash_balance,
        "upi": starting_balance.upi_balance,
    }

    required_data["daily_breakdown"] = list(daily_data)

    required_data["totals"] = totals

    required_data["ending_balance"] = ending_balances

    return required_data
