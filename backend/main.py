from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import ENVIRONMENT
from .routers import auth, categories, reports, starting_balances, transactions

app = FastAPI(
    title="Expense Tracker API",
    docs_url="/docs" if ENVIRONMENT == "dev" else None,
    redoc_url="/redoc" if ENVIRONMENT == "dev" else None,
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(starting_balances.router)
app.include_router(transactions.router)
app.include_router(reports.router)


origins = [
    "https://personal-expense-tracker-self-mu.vercel.app/"
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Website running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
