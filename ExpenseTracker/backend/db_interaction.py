'''
Script to demonstrate CRUD - Create Read Update Delete with MySQL database in python.
'''
import asyncio
import pwd
from typing import Tuple, List
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from ExpenseTracker.backend.logging_setup import setup_logger
from datetime import date
from fastapi import HTTPException
from ExpenseTracker.backend.auth import hash_password, verify_password
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from ExpenseTracker.backend.models import Expense,LoggedUsers
from sqlalchemy import select, delete, func, desc

# loads .env file
load_dotenv()

DATABASE_URL = (
    f"mysql+asyncmy://{os.getenv('DB_USER')}:{os.getenv('MYSQL_password')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

# create database manager that maintains a pool of reusable connections that a request can borrow from and return it back to pool once done.
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

# create session class - Connection + Cursor + Transaction Manager
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# create a custom logger
logger = setup_logger("db_interaction.log", "db_interaction.log", "INFO")

@asynccontextmanager
async def get_db_cursor(to_be_commited=False):
    '''
    Creates an asynchronous database session.
    :return:
    '''
    logger.info('Connecting to MySQL database')

    # This borrows from the pool of connections one connection that engine created. When done it auto returns the connection back to the pool.
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def fetch_all_records():
    '''
    Function to fetch all records from database table
    :return:
    '''
    logger.info('Fetching all records from database table')

    # fetch db cursor
    async with get_db_cursor() as session:
        # fetch all expenses using ORM
        stmt = select(Expense.id, Expense.expense_date, Expense.amount, Expense.category,Expense.notes)
        result = await session.execute(stmt)
        expenses = result.mappings().all()
        return expenses

async def fetch_expenses_for_date(expense_date: date, userid : int):
    '''
    Function to fetch all expenses for a specific user and date
    :param expense_date: Expense date
    :param userid: User ID
    :return:
    '''
    logger.info('Fetching all expenses for date')

    # fetch db cursor
    async with get_db_cursor() as session:
        # result = await session.execute(text("select * from expenses where expense_date = :expense_date and id = :id"),{"expense_date":expense_date,"id":userid})
        stmt = select(Expense.id,Expense.amount,Expense.category,Expense.notes).where(Expense.expense_date == expense_date, Expense.id == userid)
        result = await session.execute(stmt)
        expenses = result.mappings().all()
        return expenses

async def update_expenses_in_database(expenses : List[Tuple]):
    '''
    Function to update all expenses in database for the date. This initially removes all existing expenses corresponding to date
    and then puts new expenses.
    In case old records are removed while new records couldn't be added the deletion is rolled back.

    :param expense_date: Expense date
    :param userid: User ID
    :param amt: Amount spent
    :param cat: Category the amount was spent in viz. food, clothing etc.
    :param notes: Description of the expense
    :return:
    '''
    logger.info(f'Delete existing record for user {expenses[0][0]} corresponding to date {expenses[0][1]} and override new expenses')

    userid = expenses[0][0]
    expense_date = expenses[0][1]

    async with get_db_cursor() as session:
        # delete existing records if any on the date - pause coroutine whilst session executes query and commits it
        # await session.execute(text("delete from expenses where id = :id and expense_date = :expense_date;"), {"id":userid,"expense_date":expense_date})
        stmt = delete(Expense).where(Expense.id == userid and Expense.expense_date == expense_date)
        await session.execute(stmt)
        await session.commit()

        # insert new records for the date - pause the coroutine while session executes the query and commits it
        # await session.execute(text("insert into expenses (id ,expense_date, amount, category, notes) values (:id, :expense_date, :amount, :category, :notes);"),
        #                       [
        #                           {
        #                               "id":expense[0],
        #                               "expense_date":expense[1],
        #                               "amount":expense[2],
        #                               "category":expense[3],
        #                               "notes":expense[4]
        #                           }
        #                           for expense in expenses
        #                       ])
        expense_objects = [
            Expense(
                id = expense[0],
                expense_date = expense[1],
                amount = expense[2],
                category = expense[3],
                notes = expense[4]
            )
            for expense in expenses
        ]
        # no await since here SQLAlchemy simply stores the objects into its in-memory collection to be inserted later to database.
        session.add_all(expense_objects)
        await session.commit()

async def delete_records_from_database_for_a_date(expense_date,userid):
    '''
    Function to delete from database entries related to expense date.
    :param expense_date: Remove a record from database with expense date.
    :return:
    '''
    logger.info(f'Deleting data from database corresponding to expense date {expense_date} and user {userid}')

    async with get_db_cursor() as session:
        # await session.execute(text("delete from expenses where expense_date = :expense_date and id = :id;"), {"expense_date":expense_date,"id":userid})
        stmt = delete(Expense).where(Expense.id == userid,Expense.expense_date == expense_date)
        await session.execute(stmt)
        await session.commit()

async def reset_database(user_id: int):
    '''
    Function to remove all expense entries from the database corresponding to a specific user.
    :param user_id: User ID
    :return:
    '''
    logger.info('Resetting database')

    async with get_db_cursor() as session:
        # await session.execute(text("delete from expenses where id = :id;"), {"id":user_id})
        stmt = delete(Expense).where(Expense.id == user_id)
        await session.execute(stmt)
        await session.commit()

async def fetch_expenses_summary(expense_date1,expense_date2,userid : int):
    '''
    Function to fetch all expenses between two dates across different categories.
    :param expense_date1: Start date
    :param expense_date2: End date
    :param userid: User ID
    :return:
    '''

    logger.info('Fetching all expenses between dates')

    async with get_db_cursor() as session:
        # result = await session.execute(text("select category,sum(amount) as total from expenses where id = :id and expense_date between :date1 and :date2 group by category order by total desc;"),{"id":userid,"date1":expense_date1,"date2":expense_date2})
        stmt = select(Expense.category,func.sum(Expense.amount).label("total")).where(Expense.id == userid, Expense.expense_date.between(expense_date1, expense_date2)).group_by(Expense.category).order_by(desc('total'))
        result = await session.execute(stmt)
        expenses = result.mappings().all()
        return expenses

async def register_user(username,password:str):
    '''
    Function to insert new user info into database for authentication against backend-driven hashed pwd.
    In addition it also fetches database insertion failure when duplicate username is found.
    :param username:
    :param password:
    :return:
    '''
    logger.info('Inserting new user info into database')

    # store username and hashed-pwd in database. In case of duplicate username raises error.
    try:
        async with get_db_cursor() as session:
            # await session.execute(text('insert into LOGGED_USERS (USERNAME, PASSWORD) values (:username, :pwd);'), {"username":username, "pwd":hash_password(password)})
            logged_user = LoggedUsers(username=username,password=hash_password(password))
            session.add(logged_user)
            await session.commit()
    except IntegrityError as err:
        if err.orig.args[0] == 1062:
            raise HTTPException(status_code=409, detail="User already exists!. Please choose a different username!")

async def check_for_logged_user(username,pwd):
    '''
    Function to check if user exists in database. It fetches hashed pwd against user from the database
    and checks whether hashed pwd matches plain-text pwd provided by user at login time and then grants access.
    :param username:
    :param pwd:
    :return:
    '''
    logger.info('Checking if user exists in database')

    try:
        async with get_db_cursor() as session:
            # result = await session.execute(text('select USERNAME,PASSWORD,ID from LOGGED_USERS where USERNAME = :username;'), {"username":username})
            stmt = select(LoggedUsers.USERNAME,LoggedUsers.PASSWORD,LoggedUsers.ID).where(LoggedUsers.USERNAME == username)
            result = await session.execute(stmt)
            result = result.mappings().first()

        # on successful data fetch from database perform pwd and username validation
        if verify_password(pwd, result['PASSWORD']) and result['USERNAME'] == username:
            return (True, result['ID'])
        return (False, None)
    except:
        logger.exception('User not found in database.')
        raise HTTPException(status_code=404, detail="User not found in database.")

async def check_for_duplicate_username(username):
    '''
    Function that checks whether there exists duplicate username in database.
    :param username: username provided by user at the time of registration.
    :return:
    '''
    logger.info('Checking if username exists in database')
    async with get_db_cursor() as session:
        # result = await session.execute(text('select USERNAME from LOGGED_USERS where USERNAME = :username;'),{"username":username})
        stmt = select(LoggedUsers.USERNAME).where(LoggedUsers.USERNAME == username)
        result = await session.execute(stmt)
        result = result.mappings().first()

        if result:
            return True
        return False

# if __name__ == '__main__':
    # print(asyncio.run(fetch_all_records()))
    # fetch_expenses_for_date('2024-08-02')
    # insert_into_database('2025-01-01',5000.0,'Shopping','Purchased apparels')
    # delete_from_database("2025-01-01")
    # fetch_expenses_for_date('2025-01-01')
    # fetch_expenses_categorywise_between_dates("2024-08-02","2024-12-31")
    # print(asyncio.run(check_for_logged_user('sikdsou','Christiano#7')))
    # print(check_for_duplicate_username('messi'))
    # print(register_user(username="sikdsou",password="Tkinter@10"))