from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.auth.jwt import create_access_token
from backend.config import TEST_DATABASE_URL
from backend.database import Base, get_db
from backend.main import app
from backend.models import Category, StartingBalance, Transaction, User


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(url=TEST_DATABASE_URL)

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def seed_user(db_session):
    test_user = User(username="test", password="test1234", role="ADMIN")
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    return {
        "id": test_user.id,
        "username": test_user.username,
        "role": test_user.role
    }

@pytest.fixture(scope="function")
def auth_headers(seed_user):

    data = {"sub": seed_user["username"], "role": seed_user["role"]}

    token = create_access_token(data)

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def seed_categories(db_session, seed_user):
    cat1 = Category(name="food", user_id=seed_user["id"])
    cat2 = Category(name="travel", user_id=seed_user["id"])
    cat3 = Category(name="entertainment", user_id=seed_user["id"])
    db_session.add_all([cat1, cat2, cat3])
    db_session.commit()
    return [cat1, cat2, cat3]


@pytest.fixture(scope="function")
def seed_starting_balances(db_session, seed_user):
    sb1 = StartingBalance(
        month=date(2025, 12, 1),
        cash_balance=5000,
        upi_balance=15000,
        user_id=seed_user["id"],
    )
    sb2 = StartingBalance(
        month=date(2026, 2, 1),
        cash_balance=3500,
        upi_balance=12000,
        user_id=seed_user["id"],
    )
    db_session.add_all([sb1, sb2])
    db_session.commit()
    return [sb1, sb2]


@pytest.fixture(scope="function")
def seed_transactions(db_session, seed_user, seed_categories, seed_starting_balances):
    jan_txns = [
        Transaction(
            transaction_date=date(2026, 1, 5),
            description="Grocery shopping",
            amount=250,
            payment_method="CASH",
            transaction_type="EXPENSE",
            category_id=seed_categories[0].id,
            user_id=seed_user["id"],
        ),
        Transaction(
            transaction_date=date(2026, 1, 10),
            description="Electricity bill",
            amount=800,
            payment_method="UPI",
            transaction_type="EXPENSE",
            category_id=seed_categories[1].id,
            user_id=seed_user["id"]
        ),
        Transaction(
            transaction_date=date(2026, 1, 15),
            description="Freelance payment",
            amount=10000,
            payment_method="UPI",
            transaction_type="INCOME",
            user_id=seed_user["id"]
        ),
    ]

    feb_txns = [
        Transaction(
            transaction_date=date(2026, 2, 3),
            description="Coffee",
            amount=150,
            payment_method="CASH",
            transaction_type="EXPENSE",
            category_id=seed_categories[0].id,
            user_id=seed_user["id"],
        ),
        Transaction(
            transaction_date=date(2026, 2, 5),
            description="Restaurant",
            amount=450,
            payment_method="UPI",
            transaction_type="EXPENSE",
            category_id=seed_categories[0].id,
            user_id=seed_user["id"],
        ),
        Transaction(
            transaction_date=date(2026, 2, 10),
            description="Rent payment",
            amount=8000,
            payment_method="UPI",
            transaction_type="EXPENSE",
            category_id=seed_categories[1].id,
            user_id=seed_user["id"],
        ),
        Transaction(
            transaction_date=date(2026, 2, 15),
            description="Salary",
            amount=50000,
            payment_method="UPI",
            transaction_type="INCOME",
            user_id=seed_user["id"],
        ),
        Transaction(
            transaction_date=date(2026, 2, 18),
            description="Groceries",
            amount=1200,
            payment_method="CASH",
            transaction_type="EXPENSE",
            category_id=seed_categories[0].id,
            user_id=seed_user["id"],
        ),
        Transaction(
            transaction_date=date(2026, 2, 20),
            description="Transfer to wallet",
            amount=2000,
            payment_method="UPI",
            transaction_type="TRANSFER",
            is_debit=True,
            user_id=seed_user["id"],
        ),
        Transaction(
            transaction_date=date(2026, 2, 20),
            description="Transfer to wallet",
            amount=2000,
            payment_method="CASH",
            transaction_type="TRANSFER",
            is_debit=False,
            user_id=seed_user["id"],
        ),
        Transaction(
            transaction_date=date(2026, 2, 25),
            description="Transport",
            amount=300,
            payment_method="CASH",
            transaction_type="EXPENSE",
            category_id=seed_categories[1].id,
            user_id=seed_user["id"],
        ),
    ]

    mar_txns = [
        Transaction(
            transaction_date=date(2026, 3, 2),
            description="Medicine",
            amount=500,
            payment_method="CASH",
            transaction_type="EXPENSE",
            category_id=seed_categories[1].id,
            user_id=seed_user["id"],
        ),
        Transaction(
            transaction_date=date(2026, 3, 10),
            description="Bonus",
            amount=5000,
            payment_method="UPI",
            transaction_type="INCOME",
            user_id=seed_user["id"],
        ),
    ]

    all_txns = jan_txns + feb_txns + mar_txns
    db_session.add_all(all_txns)
    db_session.flush()

    feb_txns[5].linked_transfer_id = feb_txns[6].id
    feb_txns[6].linked_transfer_id = feb_txns[5].id

    db_session.commit()

    for t in all_txns:
        db_session.refresh(t)

    return {
        "jan": jan_txns,
        "feb": feb_txns,
        "mar": mar_txns,
        "all": all_txns
    }
