from .database import Base, engine
from .models import StartingBalance,User,Category,Transaction

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
