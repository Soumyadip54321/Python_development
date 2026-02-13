'''
Script that sets up GPT-5.2 chatbot to be used in Simpex dashboard.
'''

import streamlit as st
from openai import OpenAI
from ExpenseTracker.backend.tool_based_sql_agent import send_response_to_user_prompt

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

    # create a session storage attribute 'message' that stores chat history if not already present.
    # if 'messages' not in st.session_state:
    #     st.session_state.messages = []


    # create chat with bot as prompted by user
    if prompt := st.chat_input('Ask anything'):
        # store user-message in chat history
        # st.session_state.messages.append({'role': 'user', 'message': prompt})

        # display user-prompt
        with st.chat_message('user'):
            st.markdown(prompt)

        # display response from GPT-model
        with st.chat_message('assistant'):
            # bot_output = client.chat.completions.create(
            #     model=st.session_state.perplexity_model,
            #     messages=[{'role': m['role'], 'content': m['message']} for m in st.session_state.messages],
            #     stream=True,
            # )
            st.write_stream(send_response_to_user_prompt(prompt, userid))

        # add bot-response to chat history
        # st.session_state.messages.append({'role': 'assistant', 'message': bot_response})