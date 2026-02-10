from datetime import date
from time import sleep

import pytest
from sqlalchemy.exc import IntegrityError

# transaction_date,description,amount,payment_method,transaction_type|category_id,linked_transfer_id,is_debit
from backend.models import Category, Transaction


@pytest.fixture(scope="function")
def sample_category(db_session):
    cat1 = Category(name="Food")
    db_session.add(cat1)
    db_session.commit()
    return cat1


def test_create_income_transaction(db_session, sample_category):
    transaction = Transaction(
        transaction_date=date(2006, 2, 9),
        description="Paid off student debt",
        amount=25000,
        payment_method="upi",
        transaction_type="income",
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.id is not None


def test_create_expense_transaction(db_session, sample_category):
    transaction = Transaction(
        transaction_date=date(2006, 2, 9),
        description="Paid off student debt",
        amount=25000,
        payment_method="upi",
        transaction_type="expense",
        category_id=sample_category.id,
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.id is not None


def test_create_transfer_transaction(db_session):
    t1 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="testing transfer",
        amount=25000,
        payment_method="upi",
        transaction_type="transfer",
        linked_transfer_id=None,
        is_debit=True,
    )
    db_session.add(t1)
    db_session.flush()

    t2 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="testing transfer",
        amount=25000,
        payment_method="cash",
        transaction_type="transfer",
        linked_transfer_id=None,
        is_debit=False,
    )
    db_session.add(t2)
    db_session.flush()

    t1.linked_transfer_id = t2.id
    t2.linked_transfer_id = t1.id

    db_session.commit()

    assert t1.linked_transfer_id == t2.id
    assert t2.linked_transfer_id == t1.id


def test_normalize_transaction_type(db_session):
    transaction = Transaction(
        transaction_date=date(2006, 2, 9),
        description="Paid off student debt",
        amount=25000,
        payment_method="upi",
        transaction_type="income",
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.transaction_type == "INCOME"


def test_normalize_payment_method(db_session):
    transaction = Transaction(
        transaction_date=date(2006, 2, 9),
        description="Paid off student debt",
        amount=25000,
        payment_method="upi",
        transaction_type="income",
    )
    db_session.add(transaction)
    db_session.commit()

    assert transaction.payment_method == "UPI"


def test_reject_negative_amount(db_session):
    transaction = Transaction(
        transaction_date=date(2006, 2, 9),
        description="Paid off student debt",
        amount=-25000,
        payment_method="upi",
        transaction_type="income",
    )
    with pytest.raises(IntegrityError):
        db_session.add(transaction)
        db_session.commit()


def test_reject_expenses_without_category(db_session):
    transaction = Transaction(
        transaction_date=date(2006, 2, 9),
        description="Paid off student debt",
        amount=25000,
        payment_method="upi",
        transaction_type="expense",
    )
    with pytest.raises(IntegrityError):
        db_session.add(transaction)
        db_session.commit()


def test_invalid_payment_method(db_session):
    t1 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="testing",
        amount=25000,
        payment_method="now",
        transaction_type="income",
    )
    with pytest.raises(IntegrityError):
        db_session.add(t1)
        db_session.commit()


def test_invalid_transaction_type(db_session):
    t1 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="testing",
        amount=25000,
        payment_method="upi",
        transaction_type="noway",
    )
    with pytest.raises(IntegrityError):
        db_session.add(t1)
        db_session.commit()


def test_reject_transfer_without_is_debit(db_session):
    t1 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="testing transfer",
        amount=25000,
        payment_method="upi",
        transaction_type="transfer",
        linked_transfer_id=None,
    )
    with pytest.raises(IntegrityError):
        db_session.add(t1)
        db_session.commit()


def test_reject_non_transfer_with_is_debit(db_session):
    t1 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="testing",
        amount=25000,
        payment_method="upi",
        transaction_type="income",
        is_debit=True,
    )
    with pytest.raises(IntegrityError):
        db_session.add(t1)
        db_session.commit()


def test_reject_non_transfer_with_linked_id(db_session):
    t1 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="testing transfer",
        amount=25000,
        payment_method="upi",
        transaction_type="transfer",
        linked_transfer_id=None,
        is_debit=True,
    )
    db_session.add(t1)
    db_session.flush()

    t2 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="testing transfer",
        amount=25000,
        payment_method="cash",
        transaction_type="income",
        linked_transfer_id=t1.id,
    )
    with pytest.raises(IntegrityError):
        db_session.add(t2)
        db_session.commit()


def test_category_relationship(db_session, sample_category):
    t1 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="Paid off student debt",
        amount=25000,
        payment_method="upi",
        transaction_type="expense",
        category_id=sample_category.id,
    )
    db_session.add(t1)
    db_session.commit()

    assert t1.category is not None
    assert t1.category.id == sample_category.id
    assert t1.category.name == "food"


def test_updating_updated_at(db_session):
    t1 = Transaction(
        transaction_date=date(2006, 2, 9),
        description="testing",
        amount=25000,
        payment_method="cash",
        transaction_type="income",
    )
    db_session.add(t1)
    db_session.commit()
    initial_time = t1.updated_at

    sleep(1)

    t1.amount = 2500
    db_session.commit()
    db_session.expire(t1)

    assert t1.updated_at > initial_time
