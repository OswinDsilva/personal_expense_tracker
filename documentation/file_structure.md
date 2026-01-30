expense-tracker/                    # Root project directory
├── backend/                        # All FastAPI backend code
│   ├── __init__.py
│   ├── main.py                     # FastAPI app entry point
│   ├── config.py                   # Configuration, env loading
│   ├── database.py                 # Database connection, SessionLocal
│   ├── dependencies.py             # FastAPI dependencies (get_db, get_current_user)
│   │
│   ├── models/                     # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   └── starting_balance.py
│   │
│   ├── schemas/                    # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   └── starting_balance.py
│   │
│   ├── routers/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── categories.py
│   │   ├── transactions.py
│   │   ├── starting_balance.py
│   │   ├── analytics.py
│   │   └── export.py
│   │
│   ├── services/                   # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── transaction_service.py
│   │   ├── balance_calculator.py
│   │   └── excel_generator.py
│   │
│   └── utils/                      # Helper functions
│       ├── __init__.py
│       ├── security.py             # JWT, password hashing
│       └── pagination.py           # Cursor pagination helpers
│
├── frontend/                       # Frontend code (add later)
│   ├── index.html
│   ├── styles.css
│   └── app.js
│   # OR React app structure
│
├── tests/                          # All tests
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_auth.py
│   ├── test_categories.py
│   ├── test_transactions.py
│   └── test_analytics.py
│
├── sql/                            # Database related
│   └── schema.sql                  # Database schema
│
├── .env                            # Environment variables (gitignored)
├── .env.example                    # Template for .env
├── .gitignore
├── .python-version                 # Python version for uv
├── pyproject.toml                  # UV project config
├── uv.lock                         # UV lock file
└── README.md