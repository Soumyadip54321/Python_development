'''
Script to demonstrate CRUD - Create Read Update Delete with MySQL database in python.
'''
import pymysql
from dotenv import load_dotenv
import os
from contextlib import contextmanager
from ExpenseTracker.backend.logging_setup import setup_logger
from datetime import date

# loads .env file
load_dotenv()

# create a custom logger
logger = setup_logger("db_interaction.log", "db_interaction.log", "INFO")

@contextmanager
def get_db_cursor(to_be_commited=False):
    '''
    Function to obtain database cursor
    :return:
    '''
    logger.info('Connecting to MySQL database')

    # establish connection with mysql database and make connection in a way that cursor returns result in dictionary format
    mysql_connection = pymysql.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_password"),
        database="expense_manager",
        cursorclass=pymysql.cursors.DictCursor
    )

    # check if connected
    try:
        # If connection succeeds put query by setting up a cursor and display results in form of dictionary
        cursor = mysql_connection.cursor()
        print("Connected to MySQL database")
        yield cursor
        # In case of any change made to the database the change is temporarily stored unless commited.
        if to_be_commited:
            mysql_connection.commit()

    except Exception as e:
        mysql_connection.rollback()
        raise e
    finally:
        # close cursor
        cursor.close()
        # close connection
        mysql_connection.close()

def fetch_all_records():
    '''
    Function to fetch all records from database table
    :return:
    '''
    logger.info('Fetching all records from database table')

    # fetch db cursor
    with get_db_cursor() as cursor:
        # fetch all expenses
        cursor.execute("select * from expenses;")
        expenses = cursor.fetchall()
        return expenses

def fetch_expenses_for_date(expense_date: date, userid : int):
    '''
    Function to fetch all expenses for a specific user and date
    :param expense_date: Expense date
    :param userid: User ID
    :return:
    '''
    logger.info('Fetching all expenses for date')

    # fetch db cursor
    with get_db_cursor() as cursor:
        # fetch all expenses
        cursor.execute("select * from expenses where expense_date = %s and id = %s;", (expense_date,userid))
        expenses = cursor.fetchall()
        return expenses

def insert_into_database(expense_date,userid,amt,cat,notes):
    '''
    Function to insert entry into database
    :param expense_date: Expense date
    :param userid: User ID
    :param amt: Amount spent
    :param cat: Category the amount was spent in viz. food, clothing etc.
    :param notes: Description of the expense
    :return:
    '''
    logger.info(f'Inserting data into database corresponding to expense date {expense_date} and user {userid}')

    with get_db_cursor(to_be_commited=True) as cursor:
        cursor.execute("insert into expenses (id ,expense_date, amount, category, notes) values (%s, %s, %s, %s, %s);", (userid,expense_date,amt,cat,notes))
        # In case of any change made to the database the change is temporarily stored unless commited.
        # cursor._connection.commit()

def delete_records_from_database_for_a_date(expense_date,userid):
    '''
    Function to delete from database entries related to expense date.
    :param expense_date: Remove a record from database with expense date.
    :return:
    '''
    logger.info(f'Deleting data from database corresponding to expense date {expense_date} and user {userid}')

    with get_db_cursor(to_be_commited=True) as cursor:
        cursor.execute("delete from expenses where expense_date = %s and id = %s;", (expense_date,userid))
        # cursor._connection.commit()

def reset_database(user_id: int):
    '''
    Function to remove all expense entries from the database corresponding to a specific user.
    :param user_id: User ID
    :return:
    '''
    logger.info('Resetting database')

    with get_db_cursor(to_be_commited=True) as cursor:
        cursor.execute("delete from expenses where id = %s;", (user_id,))
        # cursor._connection.commit()


def fetch_expenses_summary(expense_date1,expense_date2,userid : int):
    '''
    Function to fetch all expenses between two dates across different categories.
    :param expense_date1: Start date
    :param expense_date2: End date
    :param userid: User ID
    :return:
    '''

    logger.info('Fetching all expenses between dates')

    with get_db_cursor() as cursor:
        cursor.execute("select category,sum(amount) as total from expenses where id = %s and expense_date between %s and %s group by category order by total desc;",(userid,expense_date1,expense_date2,))
        expenses = cursor.fetchall()
        return expenses

def register_user(username,password):
    '''
    Function to insert new user info into database for authentication.
    :param username:
    :param password:
    :return:
    '''

    logger.info('Inserting new user info into database')

    with get_db_cursor(to_be_commited=True) as cursor:
        cursor.execute('insert into LOGGED_USERS (USERNAME, PASSWORD) values (%s, %s);', (username, password,))
        # cursor._connection.commit()

def check_for_logged_user(username,password):
    '''
    Function to check if user exists in database
    :param username:
    :param password:
    :return:
    '''
    logger.info('Checking if user exists in database')

    with get_db_cursor() as cursor:
        cursor.execute('select * from LOGGED_USERS where USERNAME = %s and PASSWORD = %s;', (username,password))
        result = cursor.fetchall()
        return result

if __name__ == '__main__':
    print(fetch_all_records())
    # fetch_expenses_for_date('2024-08-02')
    insert_into_database('2025-01-01',5000.0,'Shopping','Purchased apparels')
    # delete_from_database("2025-01-01")
    # fetch_expenses_for_date('2025-01-01')
    # fetch_expenses_categorywise_between_dates("2024-08-02","2024-12-31")
