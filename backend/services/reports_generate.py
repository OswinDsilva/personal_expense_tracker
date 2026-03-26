from io import BytesIO

from xlsxwriter import Workbook

from ..utils import map_month

def add_monthly_sheet(workbook: Workbook, data: dict, month_name: str):
    worksheet = workbook.add_worksheet()

    month_format = workbook.add_format({"bold": 1})

    headings_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
        }
    )

    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        }
    )

    date_format = workbook.add_format(
        {
            "num_format": "yyyy-mm-dd",
            "align": "center",
        }
    )

    row = 0
    col = 0

    worksheet.write(row, col, month_name, month_format)
    row += 1

    worksheet.write(row, col + 1, "CASH", headings_format)
    worksheet.write(row, col + 2, "UPI", headings_format)
    row += 1

    worksheet.write(row, col, "Starting balances", headings_format)
    worksheet.write(row, col + 1, data["starting_balance"]["cash"])
    worksheet.write(row, col + 2, data["starting_balance"]["upi"])
    row += 1

    worksheet.write(row, col, "Date", headings_format)
    worksheet.merge_range(row, col + 1, row, col + 2, "Spendings", merge_format)
    row += 1

    daily_txns = data["daily_breakdown"]

    for rec in daily_txns:
        worksheet.write(row, col, rec["transaction_date"], date_format)
        worksheet.write(row, col + 1, rec["cash_spending"])
        worksheet.write(row, col + 2, rec["upi_spending"])
        row += 1

    worksheet.autofit()


def add_yearly_sheet(workbook: Workbook, data: dict, year: int):
    worksheet = workbook.add_worksheet()

    heading_format = workbook.add_format({"bold": 1, "border": 1, "align": "center"})

    merge_format = workbook.add_format(
        {
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        }
    )

    row = 0
    col = 0

    worksheet.write(row, col, year, heading_format)
    worksheet.merge_range(row, col + 1, row, col + 2, "Spendings", merge_format)
    worksheet.merge_range(row, col + 3, row, col + 4, "Income", merge_format)
    row += 1

    worksheet.write(row, col + 1, "Cash", heading_format)
    worksheet.write(row, col + 2, "UPI", heading_format)
    worksheet.write(row, col + 3, "Cash", heading_format)
    worksheet.write(row, col + 4, "UPI", heading_format)
    row += 1

    monthly_breakdown = data["monthly_breakdown"]

    for rec in monthly_breakdown:
        worksheet.write(row, col, map_month(rec["month"]), heading_format)
        worksheet.write(row, col + 1, rec["total_spending"]["cash"])
        worksheet.write(row, col + 2, rec["total_spending"]["upi"])
        worksheet.write(row, col + 3, rec["total_income"]["cash"])
        worksheet.write(row, col + 4, rec["total_income"]["upi"])
        row += 1

    worksheet.write(row, col, "Totals", heading_format)
    worksheet.write(row, col + 1, data["total_spending"]["cash"])
    worksheet.write(row, col + 2, data["total_spending"]["upi"])
    worksheet.write(row, col + 3, data["total_income"]["cash"])
    worksheet.write(row, col + 4, data["total_income"]["upi"])
    row += 2

    worksheet.write(row, col, "Final balance", heading_format)
    row += 1

    worksheet.write(row, col, "Cash", heading_format)
    worksheet.write(row, col + 1, "UPI", heading_format)
    row += 1

    worksheet.write(row, col, data["final_balance"]["cash"])
    worksheet.write(row, col + 1, data["final_balance"]["upi"])

    worksheet.autofit()
