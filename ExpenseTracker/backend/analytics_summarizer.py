'''
Script that invokes an LLM with necessary tables as input and the LLM outputs the summary of it.
'''
import time
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from functools import lru_cache
from langchain.tools import tool
from sqlalchemy import text
import pandas as pd
from langchain.agents import create_agent

load_dotenv()

# load GPT API key
openai_api_key = os.getenv('OPENAI_API_KEY')

system_prompt = """
You are an ANALYTICS SUMMARISER.

Basis data fetched for ANY 2 DATES your task is to GIVE A SUMMARY OF THE EXPENSES OBSERVED.

You must follow the RULES below:
- NEVER WRAP * AROUND RESPONSE
- SUMMARIZE INSIGHTS drawn from data and display it in plain text and FORMAT IT NICELY across BULLET POINTS.
- REMEMBER AMOUNT IS IN Rs.
"""

# setup GPT-5.2 model to output summary
model = ChatOpenAI(
    model="gpt-5.2",
    api_key=openai_api_key,
    temperature=0.0, # higher number indicates more randomness in the model's output
    max_tokens=500, #defines the no of words in the model's response
    timeout=30, # max time in sec to wait for model's response
)

# setup summarizer agent
summarizer = create_agent(
    model=model,
    system_prompt=system_prompt,
    tools=[]
)

def draw_analytics_summary(df : pd.DataFrame):
    '''
    Function to draw analytics summary from dataframe.
    :param df:
    :return:
    '''
    # set result
    output = ""

    # convert dataframe to string that LLM's can process.
    df_text = df.to_string(index=False)

    for token,metadata in summarizer.stream({"messages":[{"role":"user","content":f'Analyze this data and provide insights:\n {df_text}'}]},stream_mode="messages"):
        node = metadata["langgraph_node"]
        content = token.content_blocks

        if node == 'model' and content and content[0].get('text', ''):
            # capture progressively increasing response
            output += content[0]['text']
            yield output
