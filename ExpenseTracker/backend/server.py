'''
Script to setup backend server using FastAPI to fetch necessary information from database.
'''
from fastapi import FastAPI, HTTPException
from datetime import date
from typing import List
from ExpenseTracker.backend import db_interaction
from pydantic import BaseModel, field_validator
import re

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

# data validation for new user registration
class RegisterNewUser(BaseModel):
    username: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls,password:str):
        '''
        Class method to validate password against user info
        :param password:
        :return:
        '''
        requirements = {
            'Password must have 8 characters': len(password) >= 8,
            'Password must have one capital letter': re.search('[A-Z]', password),
            'Password must have one small letter': re.search('[a-z]', password),
            'Password must have one digit': re.search('[0-9]', password),
            'Password must have one special character': re.search('[!@#$]', password)
        }
        errors = [req for req, result in requirements.items() if result == False or result == None]

        if errors:
            raise HTTPException(status_code=400, detail=errors)
        return password

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
    data = db_interaction.check_for_logged_user(user_info.username, user_info.password)
    if data:
        return {'result':True}
    return {'result':False}
