from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..models import StartingBalance, User
from ..schema import StartingBalanceCreate, StartingBalanceResponse, StartingBalanceUpdate

router = APIRouter(prefix="/starting-balances", tags=["starting-balances"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=StartingBalanceResponse)
def create_starting_balance(
    starting_balance: StartingBalanceCreate,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s_balance = StartingBalance(
        month=starting_balance.month,
        cash_balance=starting_balance.cash_balance,
        upi_balance=starting_balance.upi_balance,
    )

    try:
        db.add(s_balance)
        db.commit()
        db.refresh(s_balance)
        return s_balance
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Starting Balance for this month exists"
        )


@router.get("/", response_model=List[StartingBalanceResponse])
def get_all_starting_balances(
    curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    starting_balances = db.execute(select(StartingBalance)).scalars().all()

    return starting_balances


@router.get("/{year}/{month}", response_model=StartingBalanceResponse)
def get_starting_balance_by_year_month(
    year: int,
    month: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        target_date = date(year, month, 1)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid year or month:{str(e)}",
        )
    starting_balance = (
        db.execute(select(StartingBalance).filter(StartingBalance.month == target_date))
        .scalars()
        .first()
    )
    if not starting_balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No record found")
    return starting_balance


@router.get("/{id}", response_model=StartingBalanceResponse)
def get_starting_balance_by_id(
    id: int, curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    starting_balance = (
        db.execute(select(StartingBalance).filter(StartingBalance.id == id)).scalars().first()
    )
    if not starting_balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No record found")
    return starting_balance


@router.patch("/{id}", response_model=StartingBalanceResponse)
def update_starting_balance_by_id(
    id: int,
    s_balance: StartingBalanceUpdate,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    starting_balance = (
        db.execute(select(StartingBalance).filter(StartingBalance.id == id)).scalars().first()
    )

    if not starting_balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    update_fields = s_balance.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(starting_balance, field, value)

    db.commit()
    db.refresh(starting_balance)
    return starting_balance


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_starting_balance_by_id(
    id: int, curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    starting_balance = (
        db.execute(select(StartingBalance).filter(StartingBalance.id == id)).scalars().first()
    )

    if not starting_balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    db.delete(starting_balance)
    db.commit()
