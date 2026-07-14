'''
Script that sets up user authentication on login to Simpex app.
'''
import time
import streamlit as st
import requests
from ExpenseTracker.backend.fetch_userid_and_userscope_tables import fetch_userid_from_username
from pwdlib import PasswordHash
import re

API_URL = 'http://127.0.0.1:8000'
# set Argon2 pwd hasher
password_hash = PasswordHash.recommended()

def rerun_on_invalid_password(password:str):
    '''
    Function that checks if the password is less than 8 characters long and has atleast one capital, one small letter, one digit and special character (#, @, _).
    :param password:
    :return:
    '''

    requirements = {
        'Password must have 8 characters':len(password) >= 8,
        'Password must have one capital letter':re.search('[A-Z]',password),
        'Password must have one small letter':re.search('[a-z]',password),
        'Password must have one digit':re.search('[0-9]',password),
        'Password must have one special character':re.search('[!@#$]',password)
    }

    unfulfilled_requirements = [req for req, result in requirements.items() if result == False or result == None]

    if unfulfilled_requirements:
        st.markdown(f"<h6 style='color:red;text-align:center;'>Password is invalid!.Please use a valid password that satisfies the following missing requirements</h6>",unsafe_allow_html=True)

        for req in unfulfilled_requirements:
            req = "-"+req
            st.markdown(f"<h6 style='color:white;text-align:center;'>{req}</h6>",unsafe_allow_html=True)

        st.session_state.page = 'register'
        time.sleep(5)
        st.rerun()

def rerun_on_duplicate_username(username):
    '''
    Function that checks whether a username is already taken or not. If taken it reruns and allows user to re-register with valid username.
    :param username:
    :return:
    '''

    username_info = {'username':username}

    # check for presence of same username in database. In the event same username exists the register page reloads allowing to type in a different username.
    try:
        response = requests.post(f'{API_URL}/check_for_same_username/',json=username_info)
        if response.status_code == 200:
            response = response.json()
            if response['result']:
                st.markdown("<h6 style='color:red;text-align:center;'>Username already taken!. Please register with a different username instead.</h6>",unsafe_allow_html=True)
                st.session_state.page = 'register'
                time.sleep(5)
                st.rerun()
    except requests.exceptions.ConnectionError:
        st.markdown("<h6 style='color:red;text-align:center;'>Couldn't connect to Simpex server. Please try again.</h6>",unsafe_allow_html=True)
        st.session_state.page = 'register'
        time.sleep(5)
        st.rerun()

def check_user_access(username,pwd)->bool:
    '''
    Function that checks if the user is already logged in or not by looking into database.
    :param username:
    :param password:
    :return:
    '''
    user_info = {'username':username,'password':pwd}

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

    st.markdown("<h1 style='text-align:center';><span style='font-style:italic;'>Simp</span><span style='color:red;'>ex</span> 💰</h1>",unsafe_allow_html=True)
    st.markdown("<h2 style='color:red;text-align:center;font-weight:bold;text-decoration:underline;'>Registration</h2>", unsafe_allow_html=True)

    new_user_info = {}

    with st.form(key='register_form',enter_to_submit=False,clear_on_submit=False):
        username = st.text_input(label='Username: ', value='', key='reg_user', placeholder='Type your username here')
        password = st.text_input(label='Password: ', value='', key='reg_password', placeholder='Must satisfy at least 8 characters long with one small & one big letter and one special characters (#, @, _)',type='password')

        col1, col2, col3, col4 = st.columns([3,1.5,2.5,2])
        with col2:
            submitted = st.form_submit_button(label='_Register_', type='primary')

        with col3:
            # button to take back a user to login page
            login_page_button = st.form_submit_button('_Login_',type='primary')

        if login_page_button:
            st.session_state.page = 'login'
            st.markdown("<h5 style='color:green;text-align:center;'>Redirecting to login page...</h5>", unsafe_allow_html=True)
            time.sleep(5)
            st.rerun()

        # update new user information in database upon submission
        if submitted:
            # check for username. If a username already exists in the database prompts user to enter a different username instead by reloading register page
            rerun_on_duplicate_username(username)

            # check for pwd validity. If found invalid shows what went wrong and re-runs to allow user to enter a valid pwd to register.
            rerun_on_invalid_password(password)

            # hash plain-text pwd
            hashed_pwd = password_hash.hash(password)

            new_user_info.update({'username':username,'hashed_pwd':hashed_pwd})
            response = requests.post(f'{API_URL}/register/',json=new_user_info)

            if response.status_code == 200:
                st.write(":green[You have successfully registered!]. Please log in with your credentials to Simpex.Redirecting to login.")
                st.session_state.page = 'login'
                time.sleep(5)
                st.rerun()

def login_user():
    '''
    UI Function that authenticates user and allow access to Simpex dashboard.
    It comes with a Register button so new users can register first. In case a new user does try to login the page redirects to registration.
    :return:
    '''

    st.markdown("<h1 style='text-align:center';><span style='font-style:italic;'>Simp</span><span style='color:red;'>ex</span> 💰</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:red;text-align:center;font-weight:bold;text-decoration:underline;'>Login</h2>",unsafe_allow_html=True)

    # setup login area
    with st.form(key='login_form',enter_to_submit=False,clear_on_submit=False):
        username = st.text_input(label='Username: ',value='',key='login_username',placeholder='Type your username here')
        password = st.text_input(label='Password: ', value='', key='login_password', placeholder='Must satisfy at least 8 characters long with one small & one big letter and one special characters (#, @, _)', type='password')

        col1, col2, col3, col4 = st.columns([3,1,2,2])

        with col2:
            # button for login
            login_submitted = st.form_submit_button('_Login_',type='primary')

        with col3:
            # button for redirecting to registration page
            register_page_button = st.form_submit_button('_Register_',type='primary')

        if register_page_button:
            st.session_state.page = 'register'
            st.markdown("<h5 style='color:green;text-align:center;'>Redirecting to registration page...</h5>", unsafe_allow_html=True)
            time.sleep(5)
            st.rerun()

        # On clicking the submit button perform the following actions.
        # Permit entry to already logged in users.
        if login_submitted:
            if check_user_access(username,password):
                st.session_state.authenticated = True
                st.session_state.userid = fetch_userid_from_username(username)

                st.write(":green[You have successfully logged in! Please wait while we get you in...]")
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

    # store expenses in session state variable so it survives form re-runs
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if 'userid' not in st.session_state:
        st.session_state.userid = ""

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
    st.session_state.data_loaded = False
    st.session_state.page = 'login'