from calendar import monthrange
from datetime import date, timedelta

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
    if not 1 <= month <= 12:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Month must be between 1 and 12")

    starting_balance = db.execute(
        select(StartingBalance)
        .where(StartingBalance.month <= date(year, month, 1))
        .order_by(StartingBalance.month.desc())
        .limit(1)
    ).scalar_one_or_none()

    if not starting_balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No starting balance found. Create one first.")
    
    if starting_balance.month == date(year, month, 1):
        actual_starting_cash = starting_balance.cash_balance
        actual_starting_upi = starting_balance.upi_balance
    else:
        last_day_before_requested = date(year, month, 1) - timedelta(days=1)

        calc_transactions = (
            db.execute(
                select(Transaction)
                .where(Transaction.transaction_date >= starting_balance.month)
                .where(Transaction.transaction_date <= last_day_before_requested)
            )
            .scalars()
            .all()
        )

        total_cash_net = 0
        total_upi_net = 0

        for t in calc_transactions:
            if t.payment_method == "CASH":
                if is_credit(t):
                    total_cash_net += t.amount
                else:
                    total_cash_net -= t.amount
            else:  # UPI
                if is_credit(t):
                    total_upi_net += t.amount
                else:
                    total_upi_net -= t.amount

        actual_starting_cash = starting_balance.cash_balance + total_cash_net
        actual_starting_upi = starting_balance.upi_balance + total_upi_net

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

    days_in_month = monthrange(year, month)[1]
    daily_data = {}

    for day in range(1, days_in_month + 1):
        daily_data[day] = {
            "transaction_date": date(year, month, day),
            "cash_spending": 0,
            "upi_spending": 0,
        }

    for t in transactions:
        if is_debit(t):
            day_num = t.transaction_date.day
            if t.payment_method == "CASH":
                daily_data[day_num]["cash_spending"] += t.amount
            else:
                daily_data[day_num]["upi_spending"] += t.amount

    ending_cash = actual_starting_cash + cash_income - cash_spending
    ending_upi = actual_starting_upi + upi_income - upi_spending

    return {
        "year": year,
        "month": month,
        "starting_balance": {
            "cash": actual_starting_cash,
            "upi": actual_starting_upi,
        },
        "daily_breakdown": list(daily_data.values()),
        "totals": {
            "cash_spending": cash_spending,
            "upi_spending": upi_spending,
            "cash_income": cash_income,
            "upi_income": upi_income,
        },
        "ending_balance": {
            "cash": ending_cash,
            "upi": ending_upi,
        },
    }
