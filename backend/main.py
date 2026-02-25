from fastapi import FastAPI

from .routers import auth, categories, starting_balances, transactions

app = FastAPI(title="Expense Tracker API")

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(starting_balances.router)
app.include_router(transactions.router)

@app.get("/")
async def root():
    return {"message": "Website running"}
