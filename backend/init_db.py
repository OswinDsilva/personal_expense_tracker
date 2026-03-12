from .database import Base, engine
from .models import Category, StartingBalance, Transaction, User  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
