import pytest
from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from time import sleep

# transaction_date,description,amount,payment_method,transaction_type|category_id,linked_transfer_id,is_debit
from backend.models import Transaction, Category

@pytest.fixture(scope='function')
def create_categories(db_session):
    cat1 = Category(name='Food')
    db_session.add(cat1)
    db_session.commit()
    yield

def test_create_basic_transaction(db_session,create_categories):
    transaction = Transaction(transaction_date=date(2006,2,9),description="Paid off student debt",amount=25000,payment_method='upi',transaction_type='expense',category_id='1')
    db_session.add(transaction)
    db_session.commit()

    assert transaction.id is not None
    
def test_normalize_transaction_type(db_session):
    transaction = Transaction(transaction_date=date(2006,2,9),description="Paid off student debt",amount=25000,payment_method='upi',transaction_type='income')
    db_session.add(transaction)
    db_session.commit()

    assert transaction.transaction_type == 'INCOME'

def test_normalize_payment_method(db_session):
    transaction = Transaction(transaction_date=date(2006,2,9),description="Paid off student debt",amount=25000,payment_method='upi',transaction_type='income')
    db_session.add(transaction)
    db_session.commit()

    assert transaction.payment_method == 'UPI'

def test_reject_negative_amount(db_session):
    transaction = Transaction(transaction_date=date(2006,2,9),description="Paid off student debt",amount=-25000,payment_method='upi',transaction_type='income')
    with pytest.raises(IntegrityError): 
        db_session.add(transaction)
        db_session.commit()

def test_ensure_category_exists_for_expenses(db_session,create_categories):
    transaction = Transaction(transaction_date=date(2006,2,9),description="Paid off student debt",amount=25000,payment_method='upi',category_id='1')
    with pytest.raises(IntegrityError):
        db_session.add(transaction)
        db_session.commit()

def test_invalid_payment_method(db_session):
    t1 = Transaction(transaction_date=date(2006,2,9),description="testing",amount=25000,payment_method='now',transaction_type='income')
    with pytest.raises(IntegrityError):
        db_session.add(t1)
        db_session.commit()

def test_invalid_transaction_type(db_session):
    t1 = Transaction(transaction_date=date(2006,2,9),description="testing",amount=25000,payment_method='upi',transaction_type='noway')
    with pytest.raises(IntegrityError):
        db_session.add(t1)
        db_session.commit()

def test_transfer_transaction(db_session):
    t1 = Transaction(transaction_date=date(2006,2,9),description="testing transfer",amount=25000,payment_method='upi',transaction_type='transfer',linked_transfer_id=None,is_debit=True)
    db_session.add(t1)
    db_session.flush()

    t2 = Transaction(transaction_date=date(2006,2,9),description="testing transfer",amount=25000,payment_method='cash',transaction_type='transfer',linked_transfer_id=None,is_debit=False)
    db_session.add(t2)
    db_session.flush()

    t1.linked_transfer_id = t2.id
    t2.linked_transfer_id = t1.id

    db_session.commit()

    assert t1.linked_transfer_id == t2.id
    assert t2.linked_transfer_id == t1.id

def test_check_is_debit_when_transfer(db_session):
    t1 = Transaction(transaction_date=date(2006,2,9),description="testing transfer",amount=25000,payment_method='upi',transaction_type='transfer',linked_transfer_id=None)
    with pytest.raises(IntegrityError):
        db_session.add(t1)
        db_session.commit()

def test_no_is_debit_without_transfer(db_session):
    t1 = Transaction(transaction_date=date(2006,2,9),description="testing",amount=25000,payment_method='upi',transaction_type='income',is_debit=True)
    with pytest.raises(IntegrityError):
        db_session.add(t1)
        db_session.commit()

def test_no_link_id_without_transfer(db_session):
    t1 = Transaction(transaction_date=date(2006,2,9),description="testing transfer",amount=25000,payment_method='upi',transaction_type='transfer',linked_transfer_id=None,is_debit=True)
    db_session.add(t1)
    db_session.flush()

    t2 = Transaction(transaction_date=date(2006,2,9),description="testing transfer",amount=25000,payment_method='cash',transaction_type='income',linked_transfer_id=t1.id)
    with pytest.raises(IntegrityError):
        db_session.add(t2)
        db_session.commit()

def test_updating_updated_at(db_session):
    t1 = Transaction(transaction_date=date(2006,2,9),description="testing transfer",amount=25000,payment_method='cash',transaction_type='income')
    db_session.add(t1)
    db_session.commit()

    initial_time = t1.updated_at
    print(initial_time)
    
    sleep(5)

    t1.amount = 2500
    assert db_session.is_modified(t1, include_collections=False)
    db_session.flush()
    db_session.commit()
    db_session.refresh(t1)

    new_time = t1.updated_at
    print(new_time)

    assert new_time > initial_time



