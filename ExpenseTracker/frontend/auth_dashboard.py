'''
Script that sets up user authentication on login to Simpex app.
'''
import time
import streamlit as st
import requests

API_URL = 'http://127.0.0.1:8000'

def check_user_access(username,password)->bool:
    '''
    Function that checks if the user is already logged in or not by looking into database.
    :param username:
    :param password:
    :return:
    '''
    user_info = {'username':username,'password':password}

    # check for user details in database
    response = requests.post(f'{API_URL}/login/',json=user_info)
    if response.status_code == 200:
        is_logged_in = response.json()
        return is_logged_in['result']

    return False

def register_user():
    '''
    UI Function that registers the user with Simpex app with username & password.
    Here new user credentials are inserted into the database.
    :return:
    '''

    st.title("_Simp_:red[ex] Registration")
    st.subheader("Your one stop solution for daily budgeting and hospital needs")

    new_user_info = {}

    with st.form(key='register_form',enter_to_submit=False,clear_on_submit=True):
        username = st.text_input(label='Username: ', value='', key='reg_user', placeholder='Type your username here')
        password = st.text_input(label='Password: ', value='', key='reg_password', placeholder='Type your password here')

        submitted = st.form_submit_button(label='_Register_', help='Register on Simpex.', type='primary')

        # update new user information in database upon submission
        if submitted:
            new_user_info.update({'username':username,'password':password})
            response = requests.post(f'{API_URL}/register/',json=new_user_info)

            if response.status_code == 200:
                st.write(":green[You have successfully registered!]. Please log in with your credentials to Simpex.Redirecting to login.")
                st.session_state.page = 'login'
                time.sleep(5)
                st.rerun()

def login_user():
    '''
    UI Function that authenticates user and allow access to Simpex dashboard.
    :param username:
    :param password:
    :return:
    '''

    st.title("_Simp_:red[ex] 💰")
    st.subheader("Your one stop solution for daily budgeting and hospital needs")

    # setup login area
    with st.form(key='login_form',enter_to_submit=False,clear_on_submit=True):
        username = st.text_input(label='Username: ',value='',key='login_username',placeholder='Type your username here')
        password = st.text_input(label='Password: ', value='', key='login_password', placeholder='Type your password here')

        submitted = st.form_submit_button('_Login_',type='primary')

        # On clicking the submit button perform the following actions.
        # Permit entry to already logged in users.
        if submitted:
            if check_user_access(username,password):
                st.session_state.authenticated = True
                st.write(":green[You have successfully logged in!]")
                time.sleep(5)
                st.rerun()
            # Ask user to register and re-login to simpex
            else:
                st.error(":red[User not found. Please register first. Redirecting to Registration....]")
                st.session_state.page = 'register'
                time.sleep(5)
                st.rerun()

def authenticate_user():
    '''
    Function that authenticates user and allow access to Simpex dashboard. In the event any user isn't logged in user registers and re-login.
    :return:
    '''
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if 'page' not in st.session_state:
        st.session_state.page = 'login'

    # page routing to dashboard for authenticated users.
    if st.session_state.authenticated:
        return True

    # Display login UI by default
    if st.session_state.page == 'login':
        login_user()
    else:
        register_user()

    return False

def logout_user():
    '''
    Function that logs out user and redirects to login screen.
    :return:
    '''

    # remove all session state attributes and rerun script.
    st.session_state.authenticated = False
    st.session_state.page = 'login'