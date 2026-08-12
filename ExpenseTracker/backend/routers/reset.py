'''
Script that holds all routes related to resetting expenses for a user.
'''
from fastapi import APIRouter, Depends
from ExpenseTracker.backend.auth import verify_access_token
from typing import Annotated
from ExpenseTracker.backend import db_interaction

# create reset routes prefixed with "/reset" and user specific JWT verification dependency injected
router = APIRouter(prefix="/reset",tags=["reset"],dependencies=[Depends(verify_access_token)])

@router.post("/reset/")
async def reset_database(userid: Annotated[int, Depends(verify_access_token)]):
    '''
    Resets database using API.
    :param userid: User ID fetched from JWT token.
    :return:
    '''
    await db_interaction.reset_database(userid)
    return {"message": "database reset successfully"}