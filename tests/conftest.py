from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.auth.jwt import create_access_token
from backend.config import TEST_DATABASE_URL
from backend.database import Base, get_db
from backend.main import app
from backend.models import Category, StartingBalance, User


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
def auth_headers(db_session):
    test_user = User(username="test", password="test1234", role="ADMIN")
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    data = {"sub": test_user.username, "role": test_user.role}

    token = create_access_token(data)

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def seed_categories(db_session):
    cat1 = Category(name="food")
    cat2 = Category(name="travel")
    cat3 = Category(name="entertainment")
    db_session.add_all([cat1, cat2, cat3])
    db_session.commit()
    return [cat1, cat2, cat3]


@pytest.fixture(scope="function")
def seed_starting_balances(db_session):
    sb1 = StartingBalance(month=date(2026, 2, 1), upi_balance=0, cash_balance=0)
    sb2 = StartingBalance(month=date(2026, 1, 1), upi_balance=0, cash_balance=0)
    sb3 = StartingBalance(month=date(2025, 12, 1), upi_balance=0, cash_balance=0)
    db_session.add_all([sb1, sb2, sb3])
    db_session.commit()
    return [sb1, sb2, sb3]
