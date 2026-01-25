'''
Script to setup backend server using FastAPI to fetch necessary information from database.
'''
from fastapi import FastAPI
from datetime import date
from typing import List

import db_interaction
from pydantic import BaseModel

# data validation for data fetched from database.
class Expense(BaseModel):
    id: int
    amount: float
    category: str
    notes: str

# data validation for new entry in database.
class Expenses_posted(BaseModel):
    amount: float
    category: str
    notes: str

    # checks for extra fields apart from the aforementioned ones and triggers failure when detected.
    model_config = {
        'extra' : 'forbid'
    }

# data validation for analytics tab
class DateRange(BaseModel):
    start: date
    end: date

class UserInfo(BaseModel):
    username: str
    password: str

# initialize fastapi object
app = FastAPI()

@app.get("/expenses/{expense_date}",response_model = List[Expense])
def get_expenses(expense_date: date):
    '''
    Fetches all expenses for a specific date using API.
    :param expense_date:
    :return:
    '''
    # fetch all data from the server
    data = db_interaction.fetch_expenses_for_date(expense_date)

    if data:
        return data
    return {"message": "No expenses found"}

@app.post("/expenses/{expense_date}")
def add_update_database(expense_date: date, expenses: List[Expenses_posted]):
    '''
    Creates a new expense and updates database using API. Also delete all expenses
    :param expense_date:
    :param expenses: list of expenses to add with each having parameters as indicated by pydantic
    :return:
    '''

    # delete all existing expense records for the date
    # db_interaction.delete_from_database(expense_date)

    # insert new expense records for the date.
    for expense in expenses:
        db_interaction.insert_into_database(expense_date, expense.amount, expense.category, expense.notes)

    return {"message": "expenses added successfully."}

@app.post("/analytics/")
def get_expenses_between_dates(date_range: DateRange):
    '''
    Fetches all expenses between expense dates using API.
    Here we use POST method to pass data in the body of the request.Data is validated for start & end dates such that only such dates are filtered out from the body.
    :param expense_date: Start & end dates filtered out from the body of the request via validation.
    :return:
    '''
    data = db_interaction.fetch_expenses_summary(date_range.start, date_range.end)

    if data:
        return data
    return {"message": "No expenses found"}

@app.get("/reset/")
def reset_database():
    '''
    Resets database using API.
    :return:
    '''

    db_interaction.reset_database()
    return {"message": "database reset successfully"}


@app.post("/register/")
def insert_new_user_info(user_info: UserInfo):
    '''
    Creates a new user info adhering to UserInfo class in database using API.
    :param user_info:
    :return:
    '''
    db_interaction.register_user(user_info.username, user_info.password)
    return {"message": "User registered successfully"}

@app.post("/login/")
def check_for_logged_in_user(user_info: UserInfo):
    '''
    Checks if a user is logged in database using API.
    :param user_info:
    :return:
    '''
    data = db_interaction.check_for_logged_user(user_info.username, user_info.password)
    if data:
        return {'result':True}
    return {'result':False}
