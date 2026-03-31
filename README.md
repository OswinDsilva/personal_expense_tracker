# Personal Expense Tracker

<p align="center">
	<b>A full-stack personal expense tracker — FastAPI backend with a React + Vite dashboard.</b>
</p>

<p align="center">
	<img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
	<img src="https://img.shields.io/badge/FastAPI-0.128+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
	<img src="https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
	<img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
	<img src="https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT" />
	<img src="https://img.shields.io/badge/React-19.2-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="React" />
	<img src="https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
	<img src="https://img.shields.io/badge/Tailwind_CSS-4.2-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
</p>

---

## About

Personal Expense Tracker is a full-stack application for managing personal finances across multiple payment methods (cash, UPI, etc.). Built with FastAPI and React, it provides a complete system for tracking income, expenses, and transfers with detailed reporting and analytics capabilities.

- **User Authentication**: JWT-based auth with Argon2 password hashing
- **Categories**: Full CRUD operations for transaction categories
- **Monthly Balances**: Track opening balances for cash and payment methods
- **Transactions**: Support for income, expenses, transfers, and adjustments
- **Filtering & Pagination**: Advanced cursor-based pagination with date, category, and payment method filters
- **Reports**: Monthly summaries with spending/income totals, daily breakdowns, and ending balances

The backend is built with FastAPI, SQLAlchemy, and PostgreSQL, and includes pytest-based test coverage for core routes.

---

## Features

| Feature | Description |
|---|---|
| **Authentication** | Admin registration (first user only), login, and user profile lookup |
| **Categories** | Create, list, retrieve, update, and delete expense categories |
| **Starting Balances** | Record monthly opening balances for tracking purposes |
| **Transactions** | Create and manage income, expense, transfer, and adjustment records |
| **Transfers** | Atomic two-entry transfer mechanism between payment methods |
| **Filtering** | Filter by date range, category, payment method, and transaction type |
| **Pagination** | Cursor-based pagination with configurable limits for large datasets |
| **Reports** | Monthly summaries with daily breakdowns and balance tracking |
| **Data Validation** | Pydantic schemas + database constraints for integrity |

---

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Pydantic v2
- Argon2 (`argon2-cffi`) for password hashing
- PyJWT for token handling
- pytest + httpx for tests
- Ruff for linting

---

## Project Structure

```text
personal_expense_tracker/
|- backend/             ← FastAPI application
|  |- auth/
|  |- models/
|  |- routers/
|  |- schema/
|  |- services/
|  |- utils/
|  |- config.py
|  |- database.py
|  |- init_db.py
|  `- main.py
|- frontend/            ← React + Vite dashboard (fully integrated with API)
|  |- src/
|  |  |- components/   ← Sidebar, MetricCard, Charts, TransactionList
|  |  |- data/         ← Utility functions and deprecated mock data
|  |  |- hooks/        ← useHealthCheck for backend connectivity
|  |  |- lib/          ← API client (api.js) and utilities
|  |  |- views/        ← Dashboard, Transactions, Reports, Analytics
|  |  |- App.jsx
|  |  `- index.css     
|  |- index.html
|  `- package.json
|- documentation/      
|- sql/
|- tests/
|- pyproject.toml
|- uv.lock
`- README.md
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL running locally or remotely
- A database for development and a separate database for tests

### 1. Clone

```bash
git clone <your-repo-url>
cd personal_expense_tracker
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Using `uv` (recommended, lockfile included):

```bash
uv sync
```

Or using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy `.env.example` to `.env` and set real values:

```bash
cp .env.example .env
```

Expected variables:

```env
DATABASE_URL=postgresql://username:password@localhost/dev_database
TEST_DATABASE_URL=postgresql://username:password@localhost/test_database
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
```

### 5. Initialize tables

```bash
python -m backend.init_db
```

### 6. Run the API

```bash
uvicorn backend.main:app --reload
```

Open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Frontend Setup

The frontend is a React + Vite application with a modern dark-mode design system using Tailwind CSS and Recharts for data visualization.

### Prerequisites

- Node.js 18+ and npm

### 1. Install dependencies

```bash
cd frontend
npm install
```

> **Note:** All dependencies (Tailwind CSS v4, PostCSS, Recharts, Lucide React, etc.) are specified in `package.json` and installed automatically via npm.

### 2. Start development server

```bash
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### 3. Pages

| Page | Route | Description |
|---|---|---|
| Dashboard | (default) | Balance overview, 6-month trend chart, recent transactions |
| Transactions | Sidebar → Transactions | Filterable, searchable full transaction list |
| Reports | Sidebar → Reports | Financial Excel-style data grid with summary metrics |
| Analytics | Sidebar → Analytics | Category donut chart, bar chart, and detailed spend cards |

### 4. Backend Integration

The frontend is **fully integrated with the live backend API**. All major views (Dashboard, Transactions, Reports) fetch real-time data from the backend. The app validates backend connectivity via the `/health` endpoint on startup.

API client functions are defined in `src/lib/api.js` and include:
- `getMonthlyData()` / `getYearlyData()` - Reports and dashboard data
- `getTransactions()` - Transaction list with filtering
- `getCategories()` - Category management
- Download and export functions for reports

### 5. Build for production

```bash
npm run build
```

Output is written to `frontend/dist/`.

---

## API Overview

Most routes require bearer token authentication.
Public routes are `/`, `/auth/register`, and `/auth/login`.

### Auth

- `POST /auth/register` - Register first user (admin) and get token
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user

### Categories

- `POST /categories` - Create category
- `GET /categories` - List categories
- `GET /categories/{id}` - Get category
- `PATCH /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

### Starting Balances

- `POST /starting-balances` - Create monthly starting balance
- `GET /starting-balances` - List all starting balances
- `GET /starting-balances/{year}/{month}` - Get by month
- `GET /starting-balances/{id}` - Get by id
- `PATCH /starting-balances/{id}` - Update by id
- `DELETE /starting-balances/{id}` - Delete by id

### Transactions

- `POST /transactions` - Create non-transfer transaction
- `POST /transactions/transfer` - Create linked transfer transactions
- `GET /transactions` - List/filter transactions (cursor pagination)
- `GET /transactions/{id}` - Get by id
- `PATCH /transactions/{id}` - Update by id (non-transfer only)
- `DELETE /transactions/{id}` - Delete by id (transfer deletes linked pair)

### Reports

- `GET /reports/data/{year}/{month}` - Monthly summary and daily breakdown

---

## Example Requests

### Register

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
	-H "Content-Type: application/json" \
	-d '{"username":"adminuser","password":"strongpass123"}'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
	-H "Content-Type: application/json" \
	-d '{"username":"adminuser","password":"strongpass123"}'
```

### Create Category

```bash
curl -X POST http://127.0.0.1:8000/categories \
	-H "Authorization: Bearer <TOKEN>" \
	-H "Content-Type: application/json" \
	-d '{"name":"Food"}'
```

### Create Expense Transaction

```bash
curl -X POST http://127.0.0.1:8000/transactions \
	-H "Authorization: Bearer <TOKEN>" \
	-H "Content-Type: application/json" \
	-d '{
		"transaction_date": "2026-02-24",
		"description": "Grocery shopping",
		"amount": 50,
		"payment_method": "UPI",
		"transaction_type": "EXPENSE",
		"category_id": 1
	}'
```

---

## Validation and Business Rules

- User registration is open only when no user exists.
- Username is normalized to lowercase and must be unique.
- Passwords are hashed with Argon2.
- Category names are unique and normalized to lowercase.
- Starting balance month must be the first day of a month and not in the future.
- Starting balance amounts are non-negative.
- Transaction amounts must be greater than zero.
- Future-dated transactions are rejected.
- `EXPENSE` transactions require `category_id`.
- Transfers must use different source and destination methods.
- Transfer updates are blocked; deleting one transfer record removes its linked pair.

---

## Testing

Run all tests:

```bash
pytest -q
```

Run a subset:

```bash
pytest tests/test_routers -q
```

Note: tests require `TEST_DATABASE_URL` to be configured and reachable.

---

## Linting

```bash
ruff check .
```

---

## Documentation

Additional docs are available in:

- `documentation/endpoints.md`
- `documentation/API_Documentation/api.md`
- `documentation/file_structure.md`
- `sql/schema.sql`

---

## Current Status and Future Work

**Completed:**
- ✅ Full backend API with transaction, category, and reporting functionality
- ✅ Frontend fully integrated with live backend API
- ✅ JWT authentication and user management
- ✅ Dashboard with real-time data, 6-month trend chart, and recent transactions
- ✅ Transaction filtering and pagination
- ✅ Monthly and yearly reports with export capabilities

**In Progress / Upcoming:**
1. Analytics page implementation (category trends, payment method analysis, insights)
2. Transaction create/edit UI modals (partial support exists in components)
3. Advanced export functionality (CSV/XLSX/PDF downloads)
4. Enhanced role-based access control beyond authentication
5. Additional filtering and search capabilities
6. Mobile responsive enhancements
