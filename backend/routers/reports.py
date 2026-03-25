from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..models import User
from ..schema import MonthlyDataResponse, YearlyDataResponse
from ..services import get_monthly_data_logic, get_yearly_data_logic

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/data/{year}/{month}", response_model=MonthlyDataResponse)
def get_monthly_data(
    year: int,
    month: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_monthly_data_logic(year, month, db)
    except ValueError as e:
        if "Invalid month" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Month must be between 1 and 12"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, details="Starting balances not found"
            )


@router.get("/data/{year}", response_model=YearlyDataResponse)
def get_yearly_data(
    year: int, curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        return get_yearly_data_logic(year, db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details="Starting balances not found"
        )


@router.get("/{year}/{month}")
def get_generate_monthly_report(
    year: int,
    month: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = get_monthly_data_logic(year, month, db)

    # Continue later using xlsxWriter for excel generation
