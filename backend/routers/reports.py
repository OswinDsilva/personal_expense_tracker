import io

import xlsxwriter
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..models import User
from ..schema import MonthlyDataResponse, YearlyDataResponse
from ..services import (
    add_monthly_sheet,
    add_yearly_sheet,
    get_monthly_data_logic,
    get_yearly_data_logic,
)
from ..utils import map_month

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


@router.get("/exports/{year}/full")
def get_generate_full_year_report(
    year: int, curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    buffer = io.BytesIO()

    with xlsxwriter.Workbook(buffer, {"in_memory": True}) as workbook:
        for month in range(1, 12 + 1):
            monthly_data = get_monthly_data_logic(year, month, db)

            month_name = map_month(month)
            add_monthly_sheet(workbook, monthly_data, month_name)

        yearly_data = get_yearly_data_logic(year, db)

        add_yearly_sheet(workbook, yearly_data, year)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=Expenses_{year}_full_summary.xlsx"},
    )


@router.get("/exports/{year}/{month}")
def get_generate_monthly_report(
    year: int,
    month: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not 1 <= month <= 12:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, details="Invalid month value")

    data = get_monthly_data_logic(year, month, db)

    month_name = map_month(month)

    buffer = io.BytesIO()

    with xlsxwriter.Workbook(buffer, {"in_memory": True}) as workbook:
        add_monthly_sheet(workbook, data, month_name)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=Expenses_{month_name}_{year}.xlsx"},
    )


@router.get("/exports/{year}")
def get_generate_yearly_report(
    year: int, curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    data = get_yearly_data_logic(year, db)

    buffer = io.BytesIO()

    with xlsxwriter.Workbook(buffer, {"in_memory": True}) as workbook:
        add_yearly_sheet(workbook, data, year)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=Expenses_{year}_summary.xlsx"},
    )
