from calendar import monthrange
from datetime import date

from sqlalchemy import and_, extract, select
from sqlalchemy.orm import Session

from ..models import Transaction
from ..utils import is_credit, is_debit
from .balance_calculator import starting_balance_resolver


def get_yearly_data_logic(year: int, db: Session):
    monthly_data = {}
    for month in range(1, 12 + 1):
        monthly_data[month] = {
            "month": month,
            "total_spending": {
                "cash": 0,
                "upi": 0,
            },
            "total_income": {
                "cash": 0,
                "upi": 0,
            },
            "num_txns": 0,
        }

    all_txns = (
        db.execute(
            select(Transaction)
            .where(extract("year", Transaction.transaction_date) == year)
            .order_by(Transaction.transaction_date)
        )
        .scalars()
        .all()
    )

    for t in all_txns:
        monthly_data[t.transaction_date.month]["num_txns"] += 1
        if is_debit(t):
            if t.payment_method == "UPI":
                monthly_data[t.transaction_date.month]["total_spending"]["upi"] += t.amount
            else:
                monthly_data[t.transaction_date.month]["total_spending"]["cash"] += t.amount
        else:
            if t.payment_method == "UPI":
                monthly_data[t.transaction_date.month]["total_income"]["upi"] += t.amount
            else:
                monthly_data[t.transaction_date.month]["total_income"]["cash"] += t.amount

    total_upi_spending = sum(
        t.amount for t in all_txns if t.payment_method == "UPI" and is_debit(t)
    )
    total_cash_spending = sum(
        t.amount for t in all_txns if t.payment_method == "CASH" and is_debit(t)
    )
    total_upi_income = sum(t.amount for t in all_txns if t.payment_method == "UPI" and is_credit(t))
    total_cash_income = sum(
        t.amount for t in all_txns if t.payment_method == "CASH" and is_credit(t)
    )

    total_spending = {"cash": total_cash_spending, "upi": total_upi_spending}

    total_income = {"cash": total_cash_income, "upi": total_upi_income}

    final_upi_balance = total_upi_income - total_upi_spending
    final_cash_balance = total_cash_income - total_cash_spending

    try:
        net_balance_change = starting_balance_resolver(date(year, 1, 1), db)
    except ValueError:
        raise ValueError("No starting balances")

    final_upi_balance += net_balance_change["upi"]
    final_cash_balance += net_balance_change["cash"]

    final_balance = {"cash": final_cash_balance, "upi": final_upi_balance}

    return {
        "year": year,
        "monthly_breakdown": list(monthly_data.values()),
        "total_spending": total_spending,
        "total_income": total_income,
        "final_balance": final_balance,
    }


def get_monthly_data_logic(
    year: int,
    month: int,
    db: Session,
):
    if not 1 <= month <= 12:
        raise ValueError("Invalid month")

    try:
        starting_balances = starting_balance_resolver(date(year, month, 1), db)
    except ValueError:
        raise ValueError("No starting balance")

    actual_starting_cash = starting_balances["cash"]
    actual_starting_upi = starting_balances["upi"]

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
