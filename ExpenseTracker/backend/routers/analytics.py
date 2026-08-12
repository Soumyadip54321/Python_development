'''
Script that holds all routes related to analytics.
'''
from fastapi import APIRouter, Depends
from typing import Annotated
from ExpenseTracker.backend.auth import verify_access_token
from ExpenseTracker.backend.auth import DateRange
from ExpenseTracker.backend import db_interaction

# create router for analytics prefixed with "/analytics" and user specific JWT verification dependency injected
router = APIRouter(prefix="/analytics",tags=["analytics"],dependencies=[Depends(verify_access_token)])

@router.post("/")
async def get_expenses_between_dates(date_range: DateRange, userid: Annotated[int, Depends(verify_access_token)]):
    '''
    Fetches all expenses between expense dates using API.
    Here we use POST method to pass data in the body of the request.Data is validated for start & end dates such that only such dates are filtered out from the body.
    :param date_range: Start & end dates filtered out from the body of the request via validation.
    :param userid: User ID fetched from JWT token.
    :return:
    '''
    data = await db_interaction.fetch_expenses_summary(date_range.start, date_range.end, userid)

    if data:
        return data
    return {"message": "No expenses found"}

