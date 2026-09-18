import pytest
from sqlalchemy.exc import IntegrityError

from backend.models import Category


def test_create_category(db_session, seed_user):
    category = Category(name="Food", user_id=seed_user["id"])
    db_session.add(category)
    db_session.commit()

    assert category.id is not None
    assert category.name == "food"
    assert category.created_at is not None


def test_duplicate_category_rejected(db_session, seed_user):
    category = Category(name="Food", user_id=seed_user["id"])
    db_session.add(category)
    db_session.commit()
    duplicate_category = Category(name="food", user_id=seed_user["id"])
    with pytest.raises(IntegrityError):
        db_session.add(duplicate_category)
        db_session.commit()


def test_name_normalized_to_lowercase(db_session, seed_user):
    category = Category(name="FOOD", user_id=seed_user["id"])
    db_session.add(category)
    db_session.commit()

    assert category.name == "food"


def test_category_repr(db_session, seed_user):
    category = Category(name="Food", user_id=seed_user["id"])
    db_session.add(category)
    db_session.commit()

    repr_string = repr(category)
    assert "food" in repr_string
    assert "Category" in repr_string
    assert str(category.id) in repr_string
