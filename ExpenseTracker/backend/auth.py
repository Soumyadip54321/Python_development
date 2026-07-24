'''
Script that contains all Pydantic validations.
'''
from fastapi import HTTPException, Depends
from datetime import date, timedelta, datetime
from typing import List, Annotated
from pydantic import BaseModel, field_validator
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt
import re
from fastapi.security import OAuth2PasswordBearer
from ExpenseTracker.backend.config import settings

# setup password hash instance
password_hash = PasswordHash.recommended()

# fetches token created after successful user login from header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

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

def hash_password(password:str):
    '''
    Function to hash plain-text user supplied password and return hashed password to be stored in database.
    :param password:
    :return:
    '''
    return password_hash.hash(password)

def verify_password(password:str, hashed_password:str):
    '''
    Function to check whether password used by user logging in is actually the one whose hash is stored in database.
    :param password:
    :param hashed_password:
    :return:
    '''
    return password_hash.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    '''
    Function that creates a JWT token for user considering payload information from frontend.
    Payload may contain {'sub':user ID,'role':user}. It adds to the payload "exp" that indicates expiration time
    and returns finally a JWT.
    :param data:
    :param expires_delta:
    :return:
    '''
    # makes a shallow copy of the user data from payload info.
    to_encode = data.copy()
    # set expiration time for short-access token
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)

    return encoded_jwt

def verify_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    '''
    Function that verifies access token.
    Server from [headers,payload,signature] extracts headers.payload and tries to re-compute signature using secret key. If sign matches user is allowed access to
    protected API endpoints else not.
    :param token:
    :return:
    '''
    try:
        payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.algorithm])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Couldn't validate credentials.", headers={"WWW-Authenticate": "Bearer"})

    return int(payload.get('sub'))




