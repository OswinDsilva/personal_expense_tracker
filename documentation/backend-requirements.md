# Backend Service Requirements (Kharcha Dashboard)

The frontend requires the following APIs to function correctly. These are to be implemented or mapped to existing backend logic. Until they are, the frontend will use mocked data to demonstrate the UI.

## Endpoints

### 1. `GET /api/dashboard/summary`
Returns top-level metric statistics for the main dashboard view.
**Response Body:**
```json
{
  "totalBalance": 125000.50,
  "monthlySpend": 4500.00,
  "growthPercentage": 12.5,
  "spendTrend": "up" // or "down"
}
```

### 2. `GET /api/transactions`
Retrieves a list of recent transactions.
**Query Params:** `limit` (int), `page` (int), `filter` (string)
**Response Body:**
```json
{
  "transactions": [
    {
      "id": "tx-123",
      "timestamp": "2026-03-26T10:00:00Z",
      "description": "Amazon Web Services",
      "category": "Cloud Infrastructure",
      "amount": 145.20,
      "type": "debit"
    }
  ],
  "totalCount": 145
}
```

### 3. `POST /api/transactions`
Adds a new transaction.
**Request Body:**
```json
{
  "description": "Coffee",
  "amount": 4.50,
  "type": "debit",
  "categoryId": "cat-89"
}
```

### 4. `GET /api/reports/grid`
Fetches densely packed data for the Financial Excel Grid view.
**Response Body:**
```json
{
  "headers": ["Date", "Description", "Category", "Amount", "Balance"],
  "rows": [
    ["2026-03-25", "Salary", "Income", 5000.00, 125000.50]
  ]
}
```

## Considerations
- **Authentication:** Assume JWT or session-based auth. Frontend will send standard Authorization headers.
- **Latency:** Frontend design anticipates fast responses but should handle loading states gracefully with skeleton loaders conforming to the dark theme.
