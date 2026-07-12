'''
Script to setup backend server using FastAPI to fetch necessary information from database.
'''
from fastapi import FastAPI
from datetime import date
from typing import List, Dict
from ExpenseTracker.backend import db_interaction
from pydantic import BaseModel

# data validation for data fetched from database.
class Expense(BaseModel):
    id: int
    amount: float
    category: str
    notes: str

class AddExpenseDetails(BaseModel):
    amount: float
    category: str
    notes: str

# data validation for new entry in database.
class Expenses_posted(BaseModel):
    userid: int
    expenses: List[AddExpenseDetails]

    # checks for extra fields apart from the aforementioned ones and triggers failure when detected.
    model_config = {
        'extra' : 'forbid'
    }

# data validation for analytics tab
class DateRange(BaseModel):
    start: date
    end: date
    userid: int

class RegisterUserInfo(BaseModel):
    username: str
    hashed_pwd: str

class LoginUserInfo(BaseModel):
    username: str
    password: str

# initialize fastapi object
app = FastAPI()

@app.get("/expenses/{expense_date}")
def get_expenses(expense_date: date, userid):
    '''
    Fetches all expenses for a specific date using API.
    :param expense_date: Date in ISO format
    :param user_id: User ID
    :return:
    '''
    # fetch all data from the server
    data = db_interaction.fetch_expenses_for_date(expense_date, int(userid))

    if data:
        return data
    return [{'id': int(userid), 'amount': 0, 'category': 0, 'notes': ''}]

@app.post("/expenses/{expense_date}")
def add_update_database(expense_date: date, user_expense_info: dict):
    '''
    Removes all existing expenses if present in the database & updates database with new expenses.
    :param expense_date: Date in ISO format
    :param user_expense_info: list of expenses to add with each having parameters as indicated by pydantic
    :return:
    '''

    # delete all existing expense records for the date
    db_interaction.delete_records_from_database_for_a_date(expense_date, user_expense_info['userid'])

    # insert updated expense records for the date.
    for expense_info in user_expense_info['expenses']:
        db_interaction.insert_into_database(expense_date, user_expense_info['userid'], expense_info['amount'], expense_info['category'], expense_info['notes'])

    return {"message": "expenses added successfully."}

@app.post("/analytics/")
def get_expenses_between_dates(date_range: DateRange):
    '''
    Fetches all expenses between expense dates using API.
    Here we use POST method to pass data in the body of the request.Data is validated for start & end dates such that only such dates are filtered out from the body.
    :param expense_date: Start & end dates filtered out from the body of the request via validation.
    :return:
    '''
    data = db_interaction.fetch_expenses_summary(date_range.start, date_range.end, date_range.userid)

    if data:
        return data
    return {"message": "No expenses found"}

@app.post("/reset/{userid}")
def reset_database(userid: str):
    '''
    Resets database using API.
    :return:
    '''

    db_interaction.reset_database(int(userid))
    return {"message": "database reset successfully"}


@app.post("/register/")
def insert_new_user_info(user_info: RegisterUserInfo):
    '''
    Creates a new user info with hashed pwd against it in database.
    :param user_info:
    :return:
    '''
    db_interaction.register_user(user_info.username, user_info.hashed_pwd)
    return {"message": "User registered successfully"}

@app.post("/login/")
def check_for_logged_in_user(user_info: LoginUserInfo):
    '''
    Checks if a user is logged in database using API.
    :param user_info:
    :return:
    '''
    data = db_interaction.check_for_logged_user(user_info.username, user_info.password)
    if data:
        return {'result':True}
    return {'result':False}
