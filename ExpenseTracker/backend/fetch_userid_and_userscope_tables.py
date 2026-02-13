'''
Script that fetches user id from database from username of user logged in.
'''
from langchain_community.utilities import SQLDatabase
import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

# load database credentials
db_password = os.getenv('MYSQL_password')
db_user = os.getenv('DB_USER')
db_localhost = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
uri_db_credentials = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_localhost}:{db_port}/{db_name}'

# establish database connection to use all tables listed within
db = SQLDatabase.from_uri(uri_db_credentials)

def fetch_userid_from_username(username : str):
    '''
    Function that fetches user id from username.
    The userid is used to fetch user-scoped tables which is what the LLM uses to answer user queries.
    :param username:
    :return:
    '''
    # get db engine
    engine = db._engine

    with engine.connect() as conn:
        result = conn.execute(text(" SELECT * FROM LOGGED_USERS WHERE USERNAME = :username"),{"username":username})
        userid = result.fetchone()[0]

    return userid

def create_user_views(userid : str):
    '''
    Function that creates user-scoped tables to fetch data from.
    :param userid:
    :return:
    '''
    engine = db._engine
    view_expenses = f'user_expenses_{userid}'
    view_auth = f'user_auth_{userid}'

    with engine.connect() as conn:
        conn.execute(text(f'CREATE OR REPLACE VIEW {view_expenses} AS SELECT * FROM expenses WHERE id = {userid}'))
        conn.execute(text(f"CREATE OR REPLACE VIEW {view_auth} AS SELECT * FROM LOGGED_USERS WHERE ID = {userid}"))

    return view_expenses, view_auth