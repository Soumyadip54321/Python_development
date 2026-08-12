'''
Script to setup backend server using FastAPI to fetch necessary information from database.
'''
from fastapi import FastAPI
from ExpenseTracker.backend.routers import auth,analytics,expenses,reset

# initialize fastapi object
app = FastAPI(title="Expense Tracker API",description="Backend-driven API for Expense Tracker",version="0.0.1")

# inject all routers into app
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(expenses.router)
app.include_router(reset.router)