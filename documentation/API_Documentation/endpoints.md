# Backend Endpoints (Current Implementation)

This document reflects the routes currently implemented in the backend routers.

## Base URL

- Local default: `http://localhost:8000`

## Authentication Model

- Public routes:
  - `POST /auth/register`
  - `POST /auth/login`
- Protected routes:
  - Everything else requires `Authorization: Bearer <access_token>`

---

## 1. Auth

### POST /auth/register

Registers the first user only.

Request body:

```json
{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

Validation:

- `username`: min 3, max 50
- `password`: min 8

Success response: `201 Created`

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "role": "ADMIN"
  }
}
```

Notes:

- If any user already exists, returns `403` with detail `Registration is closed`.

### POST /auth/login

Logs in an existing user.

Request body:

```json
{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

Success response: `200 OK`

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "role": "ADMIN"
  }
}
```

Common failures:

- `401 Invalid credentials`

### GET /auth/me

Returns current authenticated user.

Success response: `200 OK`

```json
{
  "id": 1,
  "username": "john_doe",
  "role": "ADMIN"
}
```

---

## 2. Categories

### GET /categories/

Returns all categories.

Success response: `200 OK` (array)

```json
[
  {
    "id": 1,
    "name": "Food",
    "created_at": "2026-03-29T10:00:00Z"
  }
]
```

### POST /categories/

Creates a category.

Request body:

```json
{
  "name": "Healthcare"
}
```

Validation:

- `name`: min 3, max 50

Success response: `201 Created`

```json
{
  "id": 7,
  "name": "Healthcare",
  "created_at": "2026-03-29T10:15:00Z"
}
```

Common failures:

- `409 Category exists`

### GET /categories/{id}

Fetches one category.

- `404 Category not found` if missing.

### PATCH /categories/{id}

Updates category name.

Request body:

```json
{
  "name": "Bills"
}
```

- `404 Category not found`
- `409 Category exists` on duplicate name

### DELETE /categories/{id}

Deletes a category.

- Success: `204 No Content`
- `404 Category not found`

---

## 3. Starting Balances

### POST /starting-balances/

Creates a monthly starting balance.

Request body:

```json
{
  "month": "2026-03-01",
  "cash_balance": 3000,
  "upi_balance": 2000
}
```

Validation:

- `month` must be first day of month (`YYYY-MM-01`)
- `month` cannot be in future
- balances must be `>= 0`

Success response: `201 Created`

```json
{
  "id": 1,
  "month": "2026-03-01",
  "cash_balance": 3000,
  "upi_balance": 2000,
  "created_at": "2026-03-29T10:30:00Z"
}
```

Common failures:

- `409 Starting Balance for this month exists`

### GET /starting-balances/

Returns all starting balance records.

### GET /starting-balances/{year}/{month}

Returns balance for a given year-month.

- `422` on invalid date input
- `404 No record found`

### GET /starting-balances/{id}

Returns one record by id.

- `404 No record found`

### PATCH /starting-balances/{id}

Partial update for `cash_balance` and/or `upi_balance`.

### DELETE /starting-balances/{id}

Deletes a starting balance record.

- Success: `204 No Content`

---

## 4. Transactions

### Enums

- `payment_method`: `CASH`, `UPI`
- `transaction_type`: `INCOME`, `EXPENSE`, `TRANSFER`, `ADJUSTMENT_CREDIT`, `ADJUSTMENT_DEBIT`

### POST /transactions/

Creates an income or expense transaction.

Request body:

```json
{
  "transaction_date": "2026-03-24",
  "description": "Lunch",
  "amount": 250,
  "payment_method": "CASH",
  "transaction_type": "EXPENSE",
  "category_id": 1
}
```

Validation highlights:

- `amount > 0`
- date cannot be future
- `EXPENSE` requires `category_id`
- `TRANSFER` is not allowed here (use transfer endpoint)

### POST /transactions/transfer

Creates a transfer as two linked transactions.

Request body:

```json
{
  "transaction_date": "2026-03-24",
  "description": "Cash to UPI",
  "amount": 500,
  "source_method": "CASH",
  "destination_method": "UPI"
}
```

Success response: `201 Created` (array of 2 transactions)

```json
[
  {
    "id": 10,
    "transaction_type": "TRANSFER",
    "payment_method": "CASH",
    "is_debit": true,
    "linked_transfer_id": 11
  },
  {
    "id": 11,
    "transaction_type": "TRANSFER",
    "payment_method": "UPI",
    "is_debit": false,
    "linked_transfer_id": 10
  }
]
```

### GET /transactions/

Cursor-paginated transaction listing.

Query params:

- `start_date` (optional, `YYYY-MM-DD`)
- `end_date` (optional, `YYYY-MM-DD`)
- `category_id` (optional)
- `transaction_type` (optional)
- `payment_method` (optional)
- `cursor` (optional, format `YYYY-MM-DD_ID`)
- `limit` (optional, default 50, range 1..100)

Success response:

```json
{
  "data": [
    {
      "id": 101,
      "transaction_date": "2026-03-24",
      "description": "Groceries",
      "amount": 1200,
      "payment_method": "UPI",
      "transaction_type": "EXPENSE",
      "category_id": 1,
      "linked_transfer_id": null,
      "is_debit": null,
      "created_at": "2026-03-24T10:00:00Z",
      "updated_at": "2026-03-24T10:00:00Z",
      "category": {
        "id": 1,
        "name": "Food",
        "created_at": "2026-03-01T00:00:00Z"
      }
    }
  ],
  "pagination": {
    "next_cursor": "2026-03-24_101",
    "has_more": false,
    "limit": 50
  }
}
```

### GET /transactions/{id}

Fetches one transaction.

### PATCH /transactions/{id}

Partial update for:

- `transaction_date`
- `description`
- `amount`
- `category_id`

Notes:

- Transfer transactions cannot be altered.

### DELETE /transactions/{id}

Deletes a transaction.

Notes:

- If it is linked transfer data, both linked records are removed.

---

## 5. Reports

### GET /reports/data/{year}/{month}

Returns monthly computed data.

Success response shape:

- `year`, `month`
- `starting_balance` (`cash`, `upi`)
- `daily_breakdown` (per date: `cash_spending`, `upi_spending`)
- `totals` (`cash_spending`, `upi_spending`, `cash_income`, `upi_income`)
- `ending_balance` (`cash`, `upi`)

### GET /reports/data/{year}

Returns yearly computed data.

Success response shape:

- `year`
- `monthly_breakdown` (month-wise spending/income)
- `total_spending`
- `total_income`
- `final_balance`

### GET /reports/preview/monthly/{year}/{month}

Returns spreadsheet-style monthly preview.

### GET /reports/preview/yearly/{year}

Returns spreadsheet-style yearly preview.

Preview response includes:

- `sheet_title`
- `grid` (2D array)
- `merges`
- `cell_types`
- `meta`

### GET /reports/exports/{year}/{month}

Downloads monthly XLSX.

### GET /reports/exports/{year}

Downloads yearly XLSX.

### GET /reports/exports/{year}/full

Downloads full-year XLSX (all months + yearly summary).

---

## Frontend Integration Status (Current)

- Login: wired to `POST /auth/login`
- Registration: wired to `POST /auth/register`
- Logout: implemented in frontend by clearing stored token/user
- Categories: list + create wired
- Starting balances: create wired
- Transactions: list + create wired
- Reports preview/export: monthly, yearly, full-year export wired
- Dashboard: uses live data via reports/transactions endpoints
- Analytics view: intentionally marked as under development
