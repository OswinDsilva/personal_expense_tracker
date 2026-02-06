from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select

from ..database import Base, SessionLocal, engine
from .user import User

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

ph = PasswordHasher()


def hashed(password: str) -> str:
    return ph.hash(password)


admin_user1 = User(username="Oswin", password_hash=hashed("oswin"), role="ADMIN")
user2 = User(username="Oswin", password_hash=hashed("oswin"), role="ADMIN")
user3 = User(username="Oswin", password_hash=hashed("oswin"), role="MAGICIAN")

with SessionLocal() as session:
    with session.begin():
        session.add(admin_user1)
    SELECT_QUERY = select(User)
    rows = session.execute(SELECT_QUERY).scalars().all()
    print(f"DEBUG: Found {len(rows)} rows INSIDE transaction")

    retrieved_user = session.get(User, 1)
    try:
        ph.verify(retrieved_user.password_hash, "oswin")
        print(True)
    except VerifyMismatchError:
        print(False)
    except Exception as e:
        print(f"Error:{e}")
    for row in rows:
        print(row)
