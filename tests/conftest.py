import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.config import TEST_DATABASE_URL
from backend.database import Base


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
