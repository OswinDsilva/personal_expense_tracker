from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from ..config import JWT_ALGORITHM, JWT_EXPIRATION_DAYS, JWT_SECRET_KEY
from ..database import get_db
from ..models import User

security = HTTPBearer()

"""
data = {
    "sub" : username,
    "role" : user_role
}
"""


def create_access_token(data: dict) -> str:
    payload = data.copy()
    now = datetime.now(tz=timezone.utc)
    payload["iat"] = now
    payload["exp"] = now + timedelta(days=JWT_EXPIRATION_DAYS)

    token = jwt.encode(payload=payload, algorithm=JWT_ALGORITHM, key=JWT_SECRET_KEY)

    return token


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials

    payload = verify_access_token(token)

    username = payload["sub"]

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
