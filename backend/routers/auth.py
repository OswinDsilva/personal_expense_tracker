from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.jwt import create_access_token, get_current_user
from ..database import get_db
from ..models import User
from ..schema import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).first()

    if user is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Registration is closed")

    user = User(username=req.username, password=req.password, role="ADMIN")
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username, "role": user.role})

    return TokenResponse(
        access_token=token, token_type="bearer", user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    try:
        user.verify_password(plain_password=req.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "role": user.role})

    return TokenResponse(
        access_token=token, token_type="bearer", user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
