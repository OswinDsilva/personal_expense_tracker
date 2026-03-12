# Personal Expense Tracker API

<p align="center">
	<b>A backend-first personal expense tracker with JWT auth, category management, starting balances, transactions, and monthly reporting.</b>
</p>

<p align="center">
	<img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
	<img src="https://img.shields.io/badge/FastAPI-0.128+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
	<img src="https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
	<img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
	<img src="https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT" />
</p>

---

## About

This project is a backend API for tracking personal finances across cash and UPI accounts. It supports:

- User authentication with JWT
- Category CRUD
- Monthly starting balance records
- Income, expense, transfer, and adjustment transactions
- Cursor-based transaction pagination with filters
- Monthly reports with spending/income totals and ending balances

The backend is built with FastAPI, SQLAlchemy, and PostgreSQL, and includes pytest-based test coverage for core routes.

---

## Features

| Feature | Description |
|---|---|
| Authentication | First-user admin registration, login, and current-user lookup (`/auth/me`) |
| Categories | Create, list, retrieve, update, and delete categories |
| Starting Balances | Store monthly opening balances (first day of month only) |
| Transactions | Create and manage income/expense/adjustment entries |
| Transfers | Atomic two-record transfer flow between payment methods |
| Filtering | Filter transactions by date range, category, payment method, and type |
| Pagination | Cursor-based pagination for transactions (`cursor`, `limit`) |
| Reports | Monthly aggregates and daily spending breakdown |
| Validation | Pydantic + DB constraints for data integrity |

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
|- backend/
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
pip install -e .
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

## Current Scope and Next Work

- `backend/routers/analytics.py` and `backend/routers/exports.py` currently exist as placeholders.
- `frontend/` is present but not yet implemented.

Potential next additions:

1. Analytics endpoints (category trend, payment-method trend, period comparisons)
2. Export endpoints (CSV/XLSX/PDF)
3. Frontend dashboard integration
4. Role-based authorization checks beyond authentication

---

## License

Add a license file (for example, MIT) if you plan to publish this repository.
