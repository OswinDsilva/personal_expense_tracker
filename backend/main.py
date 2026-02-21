from fastapi import FastAPI

from .routers import auth, categories

app = FastAPI(title="Expense Tracker API")

app.include_router(auth.router)
app.include_router(categories.router)


@app.get("/")
async def root():
    return {"message": "Website running"}
