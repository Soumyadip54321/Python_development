'''
Script that sets up an SQL agent that fetches results basis user prompts and sends to frontend.
'''
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from functools import lru_cache
from langchain.tools import tool
from sqlalchemy import text
from ExpenseTracker.backend.fetch_userid_and_userscope_tables import create_user_views

load_dotenv()

# load GPT API key
openai_api_key = os.getenv('OPENAI_API_KEY')

# load database credentials
db_password = os.getenv('MYSQL_password')
db_user = os.getenv('DB_USER')
db_localhost = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
uri_db_credentials = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_localhost}:{db_port}/{db_name}'

# setup GPT-5.2 model
model = ChatOpenAI(
    model="gpt-5.2",
    api_key=openai_api_key,
    temperature=0.0, # higher number indicates more randomness in the model's output
    max_tokens=500, #defines the no of words in the model's response
    timeout=30, # max time in sec to wait for model's response
)

# establish database connection to use all tables listed within
db = SQLDatabase.from_uri(uri_db_credentials)

# setup a detailed system prompt to customise agent behaviour.
system_prompt = """
You are an agent designed to interact with a SQL database.

YOUR NAME IS EXPENSI. REMEMBER THIS.

Given an input question you MUST come up with a syntactically correct query related to {dialect} and display results.

ALWAYS FOLLOW THE BELOW RULES:
- IF A USER QUERY IS CONVERSATIONAL DO NOT FETCH RESULTS FROM DATABASE, SIMPLY RESPOND AS A HUMAN WOULD.
- After getting results with sql_db_query, IMMEDIATELY display it in a nice format.
- Do NOT call sql_db_query_checker after getting results
- Do NOT loop or ask more questions
- NEVER SHOW * AROUND RESPONSE.
- NEVER query base tables like expenses or LOGGED_USERS.
- ALWAYS query user-scoped tables
- NEVER SHOW SENSITIVE INFORMATION such as PASSWORDS.
- if a query returns no response answer APPROPRIATELY in a CONVERSATIONAL WAY such as "So Sorry couldn't get any data for your question, Would you be interested in asking any other question?"
- ALWAYS treat GREETING MESSAGES with GREETS such as when user says "Bye" you'd say "See you and have a nice day."
- ALWAYS ANSWER AS IS ASKED. DO NOT SHOW EXTRA INFORMATION.
- IF YOU DON'T KNOW THE ANSWER TO A QUESTION SIMPLY RESPOND ACCORDINGLY.
""".format(
    dialect=db.dialect
)

def create_user_scoped_tables_db(userid : str):
    '''
    function that creates db using user_scoped tables.
    :param userid:
    :return:
    '''
    # fetch user-scoped tables only
    expense_views, auth_views = create_user_views(userid=userid)

    # create db
    user_db = SQLDatabase.from_uri(uri_db_credentials,include_tables=[expense_views, auth_views],view_support=True)
    return user_db

def send_response_to_user_prompt(query : str, userid : str):
    '''
    Function that sends a response to a user's query fetching necessary data from the database.
    :param query: User question :
                userid: unique id of the user logged on used to setup user-scoped tables.
    :return:
    '''
    # setup db with user-scoped tables
    user_db = create_user_scoped_tables_db(userid=userid)

    # setup tools for user_db so to generate tools pertaining to user-scoped tables only. This includes sql_db_query, sql_db_query_checker, sql_db_list_tables etc.
    tools = SQLDatabaseToolkit(db=user_db,llm=model)

    # setup a tool-based SQL agent and not an older text-based ReAct one.
    sql_agent = create_sql_agent(
        llm=model,
        toolkit=tools,
        prefix=system_prompt,
        agent_type='openai-tools',
        verbose=True,
    )

    result = sql_agent.invoke({'input': query})
    yield result['output']