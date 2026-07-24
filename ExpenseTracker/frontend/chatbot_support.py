'''
Script that sets up GPT-5.2 chatbot to be used in Simpex dashboard.
'''

import streamlit as st
from ExpenseTracker.backend.tool_based_sql_agent import LLM

def init_chat_state():
    '''
    Function that captures last 4 messages, chat summary & last SQL result summary for the current user session.
    :return:
    '''
    if "messages" not in st.session_state:
        st.session_state.messages = []

def trim_messages(max_messages=4):
    '''
    Function that trims all messages to only contain the last 4 by default.
    :return:
    '''

    st.session_state.messages = st.session_state.messages[max_messages:]

# display chat history on app re-run.
def display_chat_message_history_on_apprun():
    '''
    Function that displays chat message history on app re-run.
    :param:
    :return:
    '''
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['message'])

# create chat-bot integrating GPT-5.2
def chatbot_response(userid : str):
    '''
    Function that throws response to a user .
    :param: userid - unique id of the user logged onto the dashboard.
    :return:
    '''
    # initialize chat state
    init_chat_state()

    # display chat msg history on every app re-run
    display_chat_message_history_on_apprun()

    # instantiate LLM
    llm_call = LLM(userid)

    # create chat with bot as prompted by user
    if prompt := st.chat_input('Ask anything'):
        st.session_state.messages.append({'role': "user", 'message': prompt})

        # display user-prompt
        with st.chat_message('user'):
            st.markdown(prompt)

        # store short-memory
        short_memory = {
            "recent_messages":st.session_state.messages[-4:]
        }

        # display response from GPT-model
        with st.chat_message('assistant'):
            agent_response = st.write_stream(llm_call.send_response_to_user_prompt(str(prompt),short_memory))
        # store agent response
        st.session_state.messages.append({'role': "assistant", 'message': agent_response})

        # trim messages
        trim_messages()