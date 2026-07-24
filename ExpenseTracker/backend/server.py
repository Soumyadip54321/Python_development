'''
Script to setup backend server using FastAPI to fetch necessary information from database.
'''
from typing import Annotated
from fastapi import FastAPI, Depends
from datetime import date, timedelta
from ExpenseTracker.backend import db_interaction
from ExpenseTracker.backend.auth import DateRange,RegisterNewUser,LoginUserInfo,create_access_token,verify_access_token
from ExpenseTracker.backend.config import settings

# initialize fastapi object
app = FastAPI()

@app.get("/add_update_expenses/{expense_date}")
def get_expenses(expense_date: date, userid: Annotated[int, Depends(verify_access_token)]):
    '''
    Fetches all expenses for a specific date using API.
    :param expense_date: Date in ISO format
    :param userid: User ID fetched from JWT token.
    :return:
    '''
    # fetch all data from the server
    data = db_interaction.fetch_expenses_for_date(expense_date, userid)

    if data:
        return data
    return [{'id': userid, 'amount': 0, 'category': 0, 'notes': ''}]

@app.post("/expenses/{expense_date}")
def add_update_database(expense_date: date, user_expense_info: dict, userid: Annotated[int, Depends(verify_access_token)]):
    '''
    Removes all existing expenses if present in the database & updates database with new expenses.
    :param expense_date: Date in ISO format
    :param user_expense_info: list of expenses to add with each having parameters as indicated by pydantic
    :param userid: User ID fetched from JWT token.
    :return:
    '''

    # delete all existing expense records for the date
    db_interaction.delete_records_from_database_for_a_date(expense_date, userid)

    # insert updated expense records for the date.
    for expense_info in user_expense_info['expenses']:
        db_interaction.insert_into_database(expense_date, userid, expense_info['amount'], expense_info['category'], expense_info['notes'])

    return {"message": "expenses added successfully."}

@app.post("/analytics/")
def get_expenses_between_dates(date_range: DateRange, userid: Annotated[int, Depends(verify_access_token)]):
    '''
    Fetches all expenses between expense dates using API.
    Here we use POST method to pass data in the body of the request.Data is validated for start & end dates such that only such dates are filtered out from the body.
    :param date_range: Start & end dates filtered out from the body of the request via validation.
    :param userid: User ID fetched from JWT token.
    :return:
    '''
    data = db_interaction.fetch_expenses_summary(date_range.start, date_range.end, userid)

    if data:
        return data
    return {"message": "No expenses found"}

@app.post("/reset/")
def reset_database(userid: Annotated[int, Depends(verify_access_token)]):
    '''
    Resets database using API.
    :param userid: User ID fetched from JWT token.
    :return:
    '''
    db_interaction.reset_database(userid)
    return {"message": "database reset successfully"}

@app.post("/register/")
def insert_new_user_info(new_user_info: RegisterNewUser):
    '''
    Creates a new user info with backend-driven hashed pwd saved against it in database given password & username passed meets all checks.
    In case of duplicate username it raises an error returned to frontend.
    :param new_user_info: New user information passed.
    :return:
    '''

    db_interaction.register_user(new_user_info.username, new_user_info.password)
    return {"message": "User registered successfully"}

@app.post("/login/")
def check_for_logged_in_user(user_info: LoginUserInfo):
    '''
    Checks if a user is logged in database using API.
    :param user_info:
    :return:
    '''

    result,userid = db_interaction.check_for_logged_user(user_info.username, user_info.password)

    # on successful login create JWT token and send it to frontend
    access_token = create_access_token(
        data={"sub": str(userid)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": str(userid)}