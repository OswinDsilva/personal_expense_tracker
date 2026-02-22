from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..schema import TransactionCreate,TransactionResponse,TransactionUpdate

router = APIRouter(prefix="/transactions",tags=["transactions"])

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=TransactionResponse)
def testing():
    pass


@router.post("/transfer",status_code=status.HTTP_201_CREATED,response_model=TransactionResponse)
def testing2():
    pass