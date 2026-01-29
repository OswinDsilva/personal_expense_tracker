# Complete API Endpoint Design - FINAL

## 1. Authentication (2 endpoints)

### `POST /auth/register`

**Purpose:** Register new user (first user becomes admin, then disabled)  
**Authorization:** Public (but checks if users exist)

#### Request

```json
{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

#### Response

```json
{
  "id": 1,
  "username": "john_doe",
  "role": "ADMIN",
  "created_at": "2025-01-29T10:30:00Z"
}
```

#### Logic

- Check if any users exist in database
- If no users: Create with role="ADMIN"
- If users exist: Return 403 "Registration disabled"

#### Validation

- Username min 5 chars
- Password min 8 chars
- Hash password before storing

---

### `POST /auth/login`

**Purpose:** Login and get JWT token  
**Authorization:** Public

#### Request

```json
{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "ADMIN"
}
```

#### Logic

- Verify username exists
- Verify password hash matches
- Generate JWT with payload: `{user_id, username, role}`
- Return token

---

## 2. Categories (2 endpoints)

### `GET /categories`

**Purpose:** List all categories  
**Authorization:** Both admin and guest

#### Response

```json
{
  "categories": [
    {"id": 1, "name": "Food", "created_at": "2025-01-29T10:00:00Z"},
    {"id": 2, "name": "Transport", "created_at": "2025-01-29T10:00:00Z"},
    {"id": 3, "name": "Entertainment", "created_at": "2025-01-29T10:00:00Z"},
    {"id": 4, "name": "Academics", "created_at": "2025-01-29T10:00:00Z"},
    {"id": 5, "name": "Clothing", "created_at": "2025-01-29T10:00:00Z"},
    {"id": 6, "name": "Footwear", "created_at": "2025-01-29T10:00:00Z"}
  ]
}
```

---

### `POST /categories`

**Purpose:** Create new category  
**Authorization:** Admin only

#### Request

```json
{
  "name": "Healthcare"
}
```

#### Response

```json
{
  "id": 7,
  "name": "Healthcare",
  "created_at": "2025-01-29T11:00:00Z"
}
```

#### Validation

- Name cannot be empty
- Name must be unique (DB will enforce, catch and return 400)

---

## 3. Starting Balance (2 endpoints)

### `POST /starting-balance`

**Purpose:** Initialize system with starting balances (one-time only)  
**Authorization:** Admin only

#### Request

```json
{
  "month": "2025-01-01",
  "cash_balance": 3000.00,
  "upi_balance": 2000.00
}
```

#### Response

```json
{
  "id": 1,
  "month": "2025-01-01",
  "cash_balance": 3000.00,
  "upi_balance": 2000.00,
  "created_at": "2025-01-29T10:30:00Z"
}
```

#### Validation

- Check if any `starting_balance` exists → return 400 if true: "Starting balance already initialized"
- Month must be first day of month (format: `YYYY-MM-01`)
- Balances can be negative (maybe you started in debt)

---

### `GET /starting-balance`

**Purpose:** Get the initial starting balance  
**Authorization:** Both admin and guest

#### Response

Same as POST response

---

## 4. Transactions - Income/Expense (1 endpoint)

### `POST /transactions`

**Purpose:** Create income or expense transaction  
**Authorization:** Admin only

#### Request

```json
{
  "transaction_date": "2025-01-15",
  "description": "Lunch at cafe",
  "amount": 150.00,
  "payment_method": "CASH",
  "transaction_type": "EXPENSE",
  "category_id": 1
}
```

#### Response

```json
{
  "id": 101,
  "transaction_date": "2025-01-15",
  "description": "Lunch at cafe",
  "amount": 150.00,
  "payment_method": "CASH",
  "transaction_type": "EXPENSE",
  "category_id": 1,
  "linked_transfer_id": null,
  "is_debit": null,
  "created_at": "2025-01-15T14:35:00Z",
  "updated_at": "2025-01-15T14:35:00Z"
}
```

#### Validation

- Description min 10 chars (Pydantic)
- Amount > 0
- `payment_method` must be CASH or UPI
- `transaction_type` must be INCOME or EXPENSE only (not TRANSFER or ADJUSTMENT_*)
- If type=EXPENSE, `category_id` required (NOT NULL)
- If type=INCOME, `category_id` must be null

---

## 5. Transactions - Transfer (1 endpoint)

### `POST /transactions/transfer`

**Purpose:** Create transfer (creates 2 linked transactions atomically)  
**Authorization:** Admin only

#### Request

```json
{
  "amount": 500.00,
  "debit_payment_method": "CASH",
  "credit_payment_method": "UPI",
  "transaction_date": "2025-01-15",
  "description": "Cash to UPI via friend"
}
```

#### Response

```json
{
  "debit_transaction": {
    "id": 102,
    "transaction_date": "2025-01-15",
    "description": "Cash to UPI via friend",
    "amount": 500.00,
    "payment_method": "CASH",
    "transaction_type": "TRANSFER",
    "category_id": null,
    "is_debit": true,
    "linked_transfer_id": 103,
    "created_at": "2025-01-15T14:30:00Z"
  },
  "credit_transaction": {
    "id": 103,
    "transaction_date": "2025-01-15",
    "description": "Cash to UPI via friend",
    "amount": 500.00,
    "payment_method": "UPI",
    "transaction_type": "TRANSFER",
    "category_id": null,
    "is_debit": false,
    "linked_transfer_id": 102,
    "created_at": "2025-01-15T14:30:00Z"
  }
}
```

#### Validation

- `debit_payment_method` must be different from `credit_payment_method`
- Description min 10 chars
- Amount > 0
- Use database transaction to ensure both records created atomically

#### Logic

1. Begin database transaction
2. Create debit transaction (`is_debit=true`)
3. Create credit transaction (`is_debit=false`)
4. Update both with `linked_transfer_id` references
5. Commit transaction
6. If any step fails, rollback both

---

## 6. Transactions - Adjustment (1 endpoint)

### `POST /transactions/adjustment`

**Purpose:** Create adjustment transaction  
**Authorization:** Admin only

#### Request

```json
{
  "transaction_date": "2025-01-15",
  "description": "Bank reconciliation - missed transaction",
  "amount": 100.00,
  "payment_method": "UPI",
  "transaction_type": "ADJUSTMENT_CREDIT"
}
```

#### Response

```json
{
  "id": 104,
  "transaction_date": "2025-01-15",
  "description": "Bank reconciliation - missed transaction",
  "amount": 100.00,
  "payment_method": "UPI",
  "transaction_type": "ADJUSTMENT_CREDIT",
  "category_id": null,
  "linked_transfer_id": null,
  "is_debit": null,
  "created_at": "2025-01-15T16:00:00Z",
  "updated_at": "2025-01-15T16:00:00Z"
}
```

#### Validation

- `transaction_type` must be ADJUSTMENT_CREDIT or ADJUSTMENT_DEBIT only
- Description min 10 chars
- Amount > 0 (sign determined by type)

---

## 7. Transactions - List with Cursor Pagination (1 endpoint)

### `GET /transactions`

**Purpose:** List transactions with cursor-based pagination  
**Authorization:** Both admin and guest

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cursor` | string | Optional | Base64 encoded cursor from previous response |
| `limit` | integer | Optional | Default 50, max 100 |
| `transaction_type` | string | Optional | INCOME, EXPENSE, TRANSFER, ADJUSTMENT_CREDIT, ADJUSTMENT_DEBIT |
| `payment_method` | string | Optional | CASH, UPI |
| `category_id` | integer | Optional | Filter by category |
| `start_date` | date | Optional | Format: YYYY-MM-DD |
| `end_date` | date | Optional | Format: YYYY-MM-DD |

#### Response

```json
{
  "transactions": [
    {
      "id": 105,
      "transaction_date": "2025-01-20",
      "description": "Groceries",
      "amount": 450.00,
      "payment_method": "UPI",
      "transaction_type": "EXPENSE",
      "category_id": 1,
      "linked_transfer_id": null,
      "is_debit": null,
      "created_at": "2025-01-20T10:00:00Z",
      "updated_at": "2025-01-20T10:00:00Z"
    },
    {
      "id": 104,
      "transaction_date": "2025-01-19",
      "description": "Coffee",
      "amount": 120.00,
      "payment_method": "CASH",
      "transaction_type": "EXPENSE",
      "category_id": 1,
      "linked_transfer_id": null,
      "is_debit": null,
      "created_at": "2025-01-19T15:30:00Z",
      "updated_at": "2025-01-19T15:30:00Z"
    }
  ],
  "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNS0wMS0xOVQxNTozMDowMFoiLCJpZCI6MTA0fQ==",
  "has_more": true
}
```

#### Cursor Pagination Logic

- Order by: `created_at DESC, id DESC` (newest first)
- Cursor encodes: `{created_at, id}` of last item in current page
- Fetch `limit + 1` items
- If got `limit + 1` items: `has_more = true`, return only `limit` items
- Encode last item as `next_cursor`

#### Cursor Structure (before base64)

```json
{
  "created_at": "2025-01-19T15:30:00Z",
  "id": 104
}
```

---

## 8. Transactions - Get Single (1 endpoint)

### `GET /transactions/{id}`

**Purpose:** Get single transaction by ID  
**Authorization:** Both admin and guest

#### Response

```json
{
  "id": 105,
  "transaction_date": "2025-01-20",
  "description": "Groceries",
  "amount": 450.00,
  "payment_method": "UPI",
  "transaction_type": "EXPENSE",
  "category_id": 1,
  "linked_transfer_id": null,
  "is_debit": null,
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z"
}
```

#### Error Handling

- If ID doesn't exist: 404 Not Found

---

## 9. Transactions - Update (1 endpoint)

### `PUT /transactions/{id}`

**Purpose:** Update transaction  
**Authorization:** Admin only

#### Request

```json
{
  "transaction_date": "2025-01-20",
  "description": "Updated description",
  "amount": 500.00,
  "payment_method": "CASH",
  "category_id": 2
}
```

#### Response

Updated transaction object (same as GET response)

#### Validation

- Cannot change `transaction_type` (return 400 if attempted)
- Same validation as POST (description min 10 chars, amount > 0, etc.)
- If type=EXPENSE, `category_id` required

#### Special Logic for TRANSFER Transactions

- If updating a transfer transaction, update BOTH linked transactions
- Keep amounts synchronized
- Update descriptions on both
- If user changes amount on one, update both
- Use database transaction for atomicity

#### Example

User updates transfer transaction ID 102:

```json
{
  "amount": 600.00,
  "description": "Updated transfer note"
}
```

**Result:**
- Transaction 102 (debit): amount=600, description updated
- Transaction 103 (credit): amount=600, description updated
- Both updated atomically

---

## 10. Transactions - Delete (1 endpoint)

### `DELETE /transactions/{id}`

**Purpose:** Delete transaction  
**Authorization:** Admin only

#### Response

204 No Content

#### Special Logic for TRANSFER Transactions

- If deleting a transfer, delete BOTH linked transactions atomically
- Use database transaction
- Example: `DELETE /transactions/102` also deletes transaction 103

#### Error Handling

- If ID doesn't exist: 404 Not Found

---

## 11. Analytics - Current Balance (1 endpoint)

### `GET /balance/current`

**Purpose:** Get current cash and UPI balances (as of now)  
**Authorization:** Both admin and guest

#### Response

```json
{
  "cash_balance": 2350.00,
  "upi_balance": 7500.00,
  "as_of_date": "2025-01-29T10:30:00Z"
}
```

#### Calculation Logic

For CASH balance:

```
Start with starting_balance.cash_balance
+ SUM(income transactions with payment_method=CASH)
- SUM(expense transactions with payment_method=CASH)
+ SUM(transfer transactions with payment_method=CASH and is_debit=false)
- SUM(transfer transactions with payment_method=CASH and is_debit=true)
+ SUM(adjustment_credit with payment_method=CASH)
- SUM(adjustment_debit with payment_method=CASH)
```

Same logic applies for UPI balance

---

## 12. Analytics - Monthly Summary (1 endpoint)

### `GET /analytics/monthly-summary?month=2025-01`

**Purpose:** Get summary for specific month  
**Authorization:** Both admin and guest

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `month` | string | Required | Format: YYYY-MM |

#### Response

```json
{
  "month": "2025-01",
  "starting_cash_balance": 3000.00,
  "starting_upi_balance": 2000.00,
  "total_income_cash": 0.00,
  "total_income_upi": 5000.00,
  "total_expense_cash": 1500.00,
  "total_expense_upi": 2300.00,
  "total_adjustments_cash": 0.00,
  "total_adjustments_upi": 100.00,
  "ending_cash_balance": 1500.00,
  "ending_upi_balance": 6800.00
}
```

#### Calculation Logic

- **Starting balance:** Calculate from `starting_balances` + all transactions before this month
- **Income/Expense totals:** SUM all income/expense transactions in this month
- **Adjustments:** NET of adjustment_credit minus adjustment_debit
- **Ending balance:** Starting + income - expense + adjustments (transfers net to zero)

#### Validation

- Month format must be `YYYY-MM`
- Return 400 if invalid format

---

## 13. Export - Excel (1 endpoint)

### `GET /export/excel?year=2025`

**Purpose:** Generate Excel file with 13 sheets  
**Authorization:** Both admin and guest

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `year` | string | Required | Format: YYYY (e.g., 2025) |

#### Response

Binary file download

#### Headers

```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="expense_tracker_2025.xlsx"
```

#### Excel Structure

**Sheet 1: Summary (Cumulative Statistics)**

| Month | Starting UPI | Starting Cash | UPI Income | Cash Income | UPI Spendings | Cash Spendings | Final UPI | Final Cash |
|-------|--------------|----------------|-----------|-------------|---------------|----------------|-----------|-----------|
| January | 2246.2 | 3050 | 0 | 0 | 0 | 0 | 2246.2 | 3050 |
| February | 2246.2 | 3050 | 5180 | 0 | 0 | 0 | 7426.2 | 3050 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Sheets 2-13: Monthly Sheets (January-December)**

Example for JANUARY:

```
BALANCE: UPI [2246.2] CASH [3050]

DATE | UPI | SPENT ON | CASH | SPENT ON
1    | 0   | -        | 0    | -
2    | 150 | Coffee   | 0    | -
3    | 0   | -        | 200  | Groceries
...
31   | 0   | -        | 0    | -

SPENDINGS: UPI [total] CASH [total]
```

#### Logic

For each day:
- If multiple transactions: Show aggregated total and list all descriptions
- If no transactions: Show 0 and "-"

#### Validation

- Year cannot be future (year > current year → return 400)
- If year has no data: Return Excel with structure but all zeros

#### Implementation Notes

- Use `openpyxl` library
- Generate in memory (BytesIO)
- Return as StreamingResponse

---

## Summary: 17 Endpoints Total

| # | Category | Endpoint | Method | Authorization |
|---|----------|----------|--------|----------------|
| 1 | Auth | `/auth/register` | POST | Public (first user only) |
| 2 | Auth | `/auth/login` | POST | Public |
| 3 | Categories | `/categories` | GET | Admin + Guest |
| 4 | Categories | `/categories` | POST | Admin only |
| 5 | Starting Balance | `/starting-balance` | POST | Admin only |
| 6 | Starting Balance | `/starting-balance` | GET | Admin + Guest |
| 7 | Transactions | `/transactions` | POST | Admin only |
| 8 | Transactions | `/transactions/transfer` | POST | Admin only |
| 9 | Transactions | `/transactions/adjustment` | POST | Admin only |
| 10 | Transactions | `/transactions` | GET | Admin + Guest |
| 11 | Transactions | `/transactions/{id}` | GET | Admin + Guest |
| 12 | Transactions | `/transactions/{id}` | PUT | Admin only |
| 13 | Transactions | `/transactions/{id}` | DELETE | Admin only |
| 14 | Analytics | `/balance/current` | GET | Admin + Guest |
| 15 | Analytics | `/analytics/monthly-summary` | GET | Admin + Guest |
| 16 | Export | `/export/excel` | GET | Admin + Guest |
