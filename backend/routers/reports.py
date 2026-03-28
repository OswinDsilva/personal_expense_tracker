import io
from datetime import datetime, timezone

import xlsxwriter
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..models import User
from ..schema import MonthlyDataResponse, PreviewResponse, YearlyDataResponse
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
                status_code=status.HTTP_404_NOT_FOUND, detail="Starting balances not found"
            )


@router.get("/data/{year}", response_model=YearlyDataResponse)
def get_yearly_data(
    year: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_yearly_data_logic(year, db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Starting balances not found"
        )


@router.get("/exports/{year}/full")
def get_generate_full_year_report(
    year: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid month value")

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
    year: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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


@router.get("/preview/monthly/{year}/{month}", response_model=PreviewResponse)
def get_preview_monthly(
    year: int,
    month: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = get_monthly_data_logic(year, month, db)

    sheet_title = map_month(month)

    grid = []
    grid.append([sheet_title, None, None])
    grid.append([None, "CASH", "UPI"])
    grid.append(
        ["Starting balances", data["starting_balance"]["cash"], data["starting_balance"]["upi"]]
    )
    grid.append(["Date", "Spendings", None])

    daily_data = data["daily_breakdown"]

    for rec in daily_data:
        grid.append([rec["transaction_date"], rec["cash_spending"], rec["upi_spending"]])

    # 0-indexed
    merges = [{"r1": 3, "c1": 1, "r2": 3, "c2": 2, "label": "Spendings"}]

    cell_types = {"date_columns": [0], "numeric_columns": [1, 2]}

    meta = {"year": year, "month": month, "generated_at": datetime.now(timezone.utc).isoformat()}

    return {
        "sheet_title": sheet_title,
        "grid": grid,
        "merges": merges,
        "cell_types": cell_types,
        "meta": meta,
    }


@router.get("/preview/yearly/{year}", response_model=PreviewResponse)
def get_preview_yearly(
    year: int,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = get_yearly_data_logic(year, db)

    sheet_title = str(year)

    grid = []
    grid.append([sheet_title, "Spendings", None, "Income", None])
    grid.append([None, "CASH", "UPI", "CASH", "UPI"])

    monthly_data = data["monthly_breakdown"]

    for rec in monthly_data:
        grid.append(
            [
                map_month(rec["month"]),
                rec["total_spending"]["cash"],
                rec["total_spending"]["upi"],
                rec["total_income"]["cash"],
                rec["total_income"]["upi"],
            ]
        )

    grid.append(
        [
            "Totals",
            data["total_spending"]["cash"],
            data["total_spending"]["upi"],
            data["total_income"]["cash"],
            data["total_income"]["upi"],
        ]
    )

    grid.append([None, None, None, None, None])
    grid.append(["Final balance", None, None, None, None])
    grid.append(["Cash", "UPI", None, None, None])
    grid.append([data["final_balance"]["cash"], data["final_balance"]["upi"], None, None, None])

    # 0-indexed
    merges = [
        {"r1": 0, "c1": 1, "r2": 0, "c2": 2, "label": "Spendings"},
        {"r1": 0, "c1": 3, "r2": 0, "c2": 4, "label": "Income"},
    ]

    cell_types = {"date_columns": [], "numeric_columns": [1, 2, 3, 4]}

    meta = {"year": year, "generated_at": datetime.now(timezone.utc).isoformat()}

    return {
        "sheet_title": sheet_title,
        "grid": grid,
        "merges": merges,
        "cell_types": cell_types,
        "meta": meta,
    }
