'''
Script that holds all routes related to expenses.
'''
from fastapi import APIRouter, Depends
from ExpenseTracker.backend.auth import verify_access_token
from ExpenseTracker.backend import db_interaction
from datetime import date, timedelta
from typing import Annotated

# create expense routes prefixed with "/expenses" and user specific JWT verification dependency injected
router = APIRouter(prefix="/expenses",tags=["expenses"],dependencies=[Depends(verify_access_token)])

@router.get("/add_update/{expense_date}")
async def get_expenses(expense_date: date, userid: Annotated[int, Depends(verify_access_token)]):
    '''
    Fetches all expenses for a specific date using API.
    :param expense_date: Date in ISO format
    :param userid: User ID fetched from JWT token.
    :return:
    '''
    # fetch all data from the server
    data = await db_interaction.fetch_expenses_for_date(expense_date, userid)

    if data:
        return data
    return []

@router.put("/update/{expense_date}")
async def add_update_database(expense_date: date, user_expense_info: dict, userid: Annotated[int, Depends(verify_access_token)]):
    '''
    Removes all existing expenses if present in the database & updates database with new expenses for the date. In case deletion of old records happen while
    insertion of new ones fail the deletion is rolled back.
    :param expense_date: Date in ISO format
    :param user_expense_info: list of expenses to add with each having parameters as indicated by pydantic
    :param userid: User ID fetched from JWT token.
    :return:
    '''

    # prepare records to add
    expenses = [
        (
            userid,
            expense_date,
            expense_info['amount'],
            expense_info['category'],
            expense_info['notes']
         )
        for expense_info in user_expense_info['expenses']
    ]

    # remove existing expenses if any on the date and update new expense records for the date.
    await db_interaction.update_expenses_in_database(expenses)

    return {"message": "expenses added successfully."}

@router.delete("/delete/{expense_date}")
async def delete_expenses_for_a_date(expense_date: date, userid: Annotated[int, Depends(verify_access_token)]):
    '''
    Function to delete expenses for a specific date using API.
    :param expense_date:
    :param userid:
    :return:
    '''

    # delete expenses for a date
    await db_interaction.delete_records_from_database_for_a_date(expense_date, userid)
    # return success message
    return {"message": "expenses deleted"}