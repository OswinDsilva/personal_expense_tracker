# API Integration Change Plan

Date: 2026-03-28
Purpose: final agreed changes for backend endpoints and frontend wiring.

## Confirmed Decisions

1. Keep cursor-based pagination only for transactions.
2. Transaction create flow will include date, amount, description, payment method, transaction type, and category.
3. Keep reports/data endpoints as canonical debug/data-truth endpoints.
4. Use dedicated reports/preview endpoints for grid rendering.
5. Keep reports/exports endpoints for file downloads.
6. Dashboard summary endpoint is out of scope for now.

## Backend: Existing Endpoints to Keep or Adjust

### Transactions

1. Keep GET /transactions/ with cursor pagination.
2. Keep POST /transactions/ as the main create endpoint.
3. Ensure request contract used by frontend matches backend schema:
  - transaction_date
  - amount
  - description
  - payment_method
  - transaction_type
  - category_id
4. Keep GET /transactions/ response shape as data + pagination.
5. Do not add page + limit pagination.

### Reports Data (debug and verification)

1. Keep GET /reports/data/{year}/{month} for monthly canonical data.
2. Keep GET /reports/data/{year} for yearly canonical data.
3. Do not repurpose these into grid-specific presentation responses.

### Reports Export (downloads)

1. Keep GET /reports/exports/{year}/{month} for monthly export.
2. Keep GET /reports/exports/{year} for yearly export.
3. Keep GET /reports/exports/{year}/full for full 13-sheet export.

## Backend: New Endpoints to Implement

Add dedicated preview endpoints for frontend grid rendering.

1. GET /reports/preview/monthly/{year}/{month}
  - Returns grid-ready monthly preview JSON matching the monthly Excel sheet layout.
2. GET /reports/preview/yearly/{year}
  - Returns grid-ready yearly preview JSON matching the yearly Excel sheet layout.

Required preview response shape (for both preview endpoints):

{
  "sheet_title": "February" ,
  "grid": [
    ["February", null, null],
    [null, "CASH", "UPI"],
    ["Starting balances", 10000.0, 5000.0],
    ["Date", "Spendings", null],
    ["2026-02-01", 450.0, 120.0]
  ],
  "merges": [
    { "r1": 3, "c1": 1, "r2": 3, "c2": 2, "label": "Spendings" }
  ],
  "cell_types": {
    "date_columns": [0],
    "numeric_columns": [1, 2]
  },
  "meta": {
   "year": 2026,
   "month": 3,
   "generated_at": "2026-03-28T12:00:00Z"
  }
}

Notes:
1. grid is a row-major matrix that preserves exact visual row order.
2. Use null placeholders for merged/empty cells to keep column alignment.
3. merges provides merge metadata so frontend can render colspan-style cells.
4. Keep row and column indexing 0-based in merges.

Monthly preview must mirror add_monthly_sheet layout:
1. Row 0: month name in column 0.
2. Row 1: CASH and UPI headings in columns 1 and 2.
3. Row 2: Starting balances row.
4. Row 3: Date + merged Spendings header across columns 1-2.
5. Rows 4+: daily_breakdown rows with date, cash_spending, upi_spending.

Yearly preview must mirror add_yearly_sheet layout:
1. Row 0: year in column 0, merged Spendings (1-2), merged Income (3-4).
2. Row 1: Cash/UPI subheaders for both Spendings and Income groups.
3. Rows 2-13: monthly breakdown rows (Jan-Dec order).
4. Next row: Totals row.
5. One blank spacer row.
6. Final balance section with label row, subheader row (Cash/UPI), value row.

Implementation note:
Use shared report-building logic so reports/data, reports/preview, and reports/exports stay consistent and avoid duplicated formatting/business rules.

Generator source of truth:
1. backend/services/reports_generate.py:add_monthly_sheet
2. backend/services/reports_generate.py:add_yearly_sheet

## Frontend Changes Required

### Transactions View

1. Replace mock transactions with API fetch from GET /transactions/.
2. Use cursor + limit pagination only.
3. Build create transaction form with:
  - date picker
  - amount input
  - description input
  - payment method dropdown
  - transaction type dropdown
  - category dropdown
4. Send POST /transactions/ with backend field names (including category_id).
5. For list display and ordering, prefer transaction_date (not updated_at).

### Reports View (5-button behavior)

1. Button: Load Monthly Grid
  - Call GET /reports/preview/monthly/{year}/{month}
  - Render merge metadata for Spendings group header.
2. Button: Load Yearly Grid
  - Call GET /reports/preview/yearly/{year}
  - Render section breaks for Totals and Final balance block.
3. Button: Export Monthly
  - Call GET /reports/exports/{year}/{month}
4. Button: Export Yearly
  - Call GET /reports/exports/{year}
5. Button: Export Full 13-Sheet Report
  - Call GET /reports/exports/{year}/full

## Routing and Integration Notes

1. Current backend mounts routes without a global /api prefix.
2. If frontend uses /api/* paths, add either:
  - backend prefixing, or
  - frontend proxy/rewrite.
3. Ensure enum values used by frontend match backend accepted values for:
  - payment_method
  - transaction_type

## Out of Scope for This Phase

1. GET /api/dashboard/summary implementation.
2. page + limit pagination support for transactions.
