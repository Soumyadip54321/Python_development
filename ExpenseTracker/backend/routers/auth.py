'''
Script that holds all routes for user authentication.
'''
from fastapi import APIRouter
from ExpenseTracker.backend.auth import RegisterNewUser,LoginUserInfo,create_access_token
from ExpenseTracker.backend import db_interaction
from ExpenseTracker.backend.config import settings
from datetime import timedelta

router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register/")
async def insert_new_user_info(new_user_info: RegisterNewUser):
    '''
    Creates a new user info with backend-driven hashed pwd saved against it in database given password & username passed meets all checks.
    In case of duplicate username it raises an error returned to frontend.
    :param new_user_info: New user information passed.
    :return:
    '''

    await db_interaction.register_user(new_user_info.username, new_user_info.password)
    return {"message": "User registered successfully"}

@router.post("/login/")
async def check_for_logged_in_user(user_info: LoginUserInfo):
    '''
    Checks if a user is logged in database using API.
    :param user_info:
    :return:
    '''

    result,userid = await db_interaction.check_for_logged_user(user_info.username, user_info.password)

    # on successful login create JWT token and send it to frontend
    access_token = create_access_token(
        data={"sub": str(userid)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": str(userid)}