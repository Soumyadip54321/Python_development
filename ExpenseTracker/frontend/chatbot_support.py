'''
Script that sets up chatbot to be used in Simpex dashboard.
'''

import streamlit as st
from openai import OpenAI

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

# create ChatGPT-like bot
def create_perplexity_clone():
    '''
    Function that creates a Perplexity(Sonar) clone & interacts with user.
    :return:
    '''
    # set OpenAI API key, streamlit uses this to send requests to GPT-model
    client = OpenAI(api_key=st.secrets['PERPLEXITY_API_KEY'],base_url="https://api.perplexity.ai")

    # set a default model
    if 'perplexity_model' not in st.session_state:
        st.session_state.perplexity_model = 'sonar-pro'

    # create a session storage attribute 'message' that stores chat history if not already present.
    if 'messages' not in st.session_state:
        st.session_state.messages = []


    # create chat with bot as prompted by user
    if prompt := st.chat_input('Ask anything'):
        # store user-message in chat history
        st.session_state.messages.append({'role': 'user', 'message': prompt})

        # display user-prompt
        with st.chat_message('user'):
            st.markdown(prompt)

        # display response from GPT-model
        with st.chat_message('assistant'):
            bot_output = client.chat.completions.create(
                model=st.session_state.perplexity_model,
                messages=[{'role': m['role'], 'content': m['message']} for m in st.session_state.messages],
                stream=True,
            )
            bot_response = st.write_stream((chunk.choices[0].delta.content or "" for chunk in bot_output))

        # add bot-response to chat history
        st.session_state.messages.append({'role': 'assistant', 'message': bot_response})

    # display chat messages from history on app rerun
    # display_chat_message_history_on_apprun()