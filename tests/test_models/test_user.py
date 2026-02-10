import pytest
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.exc import IntegrityError

from backend.models import User


def test_create_user(db_session):
    user1 = User(username="test_user", password="test1234", role="Admin")
    db_session.add(user1)
    db_session.commit()

    assert user1.id is not None
    assert user1.created_at is not None


def test_username_normalized_to_lowercase(db_session):
    user1 = User(username="TestUser", password="test1234", role="Admin")
    db_session.add(user1)
    db_session.commit()

    assert user1.username == "testuser"


def test_duplicate_username(db_session):
    user1 = User(username="test_user", password="test1234", role="Admin")
    db_session.add(user1)
    db_session.commit()

    user2 = User(username="test_user", password="test1234", role="Admin")

    with pytest.raises(IntegrityError):
        db_session.add(user2)
        db_session.commit()


def test_invalid_role(db_session):
    user_record = User(username="test", password="test123", role="test")

    with pytest.raises(IntegrityError):
        db_session.add(user_record)
        db_session.commit()


def test_password_verification(db_session):
    user = User(username="test", password="test123", role="admin")
    db_session.add(user)
    db_session.commit()

    assert (user.verify_password("test123")) is True

    with pytest.raises(VerifyMismatchError):
        user.verify_password("test_wrong")


def test_password_hashing(db_session):
    user = User(username="test", password="test123", role="admin")
    db_session.add(user)
    db_session.commit()

    assert user.password_hash != "test123"

    assert user.password_hash.startswith("$argon2")
