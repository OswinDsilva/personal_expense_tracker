import pytest
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.exc import IntegrityError

from backend.models import User


@pytest.fixture(scope="function")
def pwd_hasher():
    pwd = PasswordHasher()
    yield pwd


def test_create_user(pwd_hasher, db_session):
    user1 = User(username="test_user", password_hash=pwd_hasher.hash("test1234"), role="Admin")
    db_session.add(user1)
    db_session.commit()

    assert user1.id is not None
    assert user1.created_at is not None


def test_username_normalized_to_lowercase(pwd_hasher, db_session):
    user1 = User(username="TestUser", password_hash=pwd_hasher.hash("test1234"), role="Admin")
    db_session.add(user1)
    db_session.commit()

    assert user1.username == "testuser"


def test_duplicate_username(pwd_hasher, db_session):
    user1 = User(username="test_user", password_hash=pwd_hasher.hash("test1234"), role="Admin")
    db_session.add(user1)
    db_session.commit()

    user2 = User(username="test_user", password_hash=pwd_hasher.hash("test1234"), role="Admin")

    with pytest.raises(IntegrityError):
        db_session.add(user2)
        db_session.commit()


def test_invalid_role(pwd_hasher, db_session):
    user_record = User(username="test", password_hash=pwd_hasher.hash("test123"), role="test")

    with pytest.raises(IntegrityError):
        db_session.add(user_record)
        db_session.commit()


def test_password_verification(pwd_hasher, db_session):
    user = User(username="test", password_hash=pwd_hasher.hash("test123"), role="admin")
    db_session.add(user)
    db_session.commit()

    assert (pwd_hasher.verify(user.password_hash, "test123")) is True

    with pytest.raises(VerifyMismatchError):
        pwd_hasher.verify(user.password_hash, "test_wrong")
