from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import StartingBalance, Transaction
from ..utils import is_credit


def starting_balance_resolver(target_date: date, db: Session):
    upi_net = 0
    cash_net = 0
    starting_balance = db.execute(
        select(StartingBalance)
        .where(StartingBalance.month <= target_date)
        .order_by(StartingBalance.month.desc())
        .limit(1)
    ).scalar_one_or_none()

    if starting_balance is None:
        raise ValueError

    if starting_balance.month == target_date:
        upi_net = starting_balance.upi_balance
        cash_net = starting_balance.cash_balance
    else:
        last_day_before_requested = target_date - timedelta(days=1)

        calc_transactions = (
            db.execute(
                select(Transaction)
                .where(Transaction.transaction_date >= starting_balance.month)
                .where(Transaction.transaction_date <= last_day_before_requested)
            )
            .scalars()
            .all()
        )

        for t in calc_transactions:
            if t.payment_method == "CASH":
                if is_credit(t):
                    cash_net += t.amount
                else:
                    cash_net -= t.amount
            else:
                if is_credit(t):
                    upi_net += t.amount
                else:
                    upi_net -= t.amount

        upi_net += starting_balance.upi_balance
        cash_net += starting_balance.cash_balance

    return {"cash": cash_net, "upi": upi_net}
