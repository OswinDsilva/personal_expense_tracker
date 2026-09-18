from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from backend.models import StartingBalance

# month, cash_balance,upi_balance


def test_create_starting_balance(db_session, seed_user):
    starting_balance = StartingBalance(month=date(2025, 2, 1), cash_balance=100, upi_balance=100, user_id=seed_user["id"])
    db_session.add(starting_balance)
    db_session.commit()

    assert starting_balance.id is not None
    assert starting_balance.created_at is not None


def test_reject_non_first_day_of_month(db_session, seed_user):
    starting_balance = StartingBalance(month=date(2025, 2, 2), cash_balance=100, upi_balance=100, user_id=seed_user["id"])
    with pytest.raises(IntegrityError):
        db_session.add(starting_balance)
        db_session.commit()


def test_reject_duplicate_month(db_session, seed_user):
    starting_balance = StartingBalance(month=date(2025, 2, 1), cash_balance=100, upi_balance=100, user_id=seed_user["id"])
    db_session.add(starting_balance)
    db_session.commit()

    duplicate_starting_balance = StartingBalance(
        month=date(2025, 2, 1), cash_balance=100, upi_balance=100, user_id=seed_user["id"]
    )
    with pytest.raises(IntegrityError):
        db_session.add(duplicate_starting_balance)
        db_session.commit()


def test_reject_negative_cash(db_session, seed_user):
    starting_balance = StartingBalance(month=date(2025, 2, 1), cash_balance=-100, upi_balance=100, user_id=seed_user["id"])
    with pytest.raises(IntegrityError):
        db_session.add(starting_balance)
        db_session.commit()


def test_reject_negative_upi(db_session, seed_user):
    starting_balance = StartingBalance(month=date(2025, 2, 1), cash_balance=100, upi_balance=-100, user_id=seed_user["id"])
    with pytest.raises(IntegrityError):
        db_session.add(starting_balance)
        db_session.commit()
