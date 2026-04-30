import requests
import streamlit as st

API_url = 'http://127.0.0.1:8000'

def reset():
    '''
    UI Function that resets/clears database corresponding to a user on Simpex dashboard.
    :return:
    '''
    with st.container(border=True):
        reset_database = st.toggle('Reset Database' ,help='This cleans up all entries in the database.')

        if reset_database:
            response = requests.post(f"{API_url}/reset")
            if response.status_code == 200:
                reset_message = response.json()
                st.write(reset_message['message'])