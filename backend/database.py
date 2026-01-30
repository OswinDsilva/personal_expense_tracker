from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import DATABASE_URL

engine = create_engine(url=DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
