'''
Script to setup the UI of Expense Tracker application.
'''

import streamlit as st
from chatbot_support import create_perplexity_clone
from auth_dashboard import authenticate_user, logout_user
from analytics_dashboard import get_analytics
from db_reset_dashboard import reset
from add_update_dashboard import add_update
# --------------------------------------------------------- Allow user access to dashboard post successful authentication --------------------------------------------------
if authenticate_user():
    # setup title & logout button added to sidebar
    st.title("_Simp_:red[ex] 💰")

    with st.sidebar:
        st.button("Logout",key='sidebar_logout_button',on_click=logout_user)

    # setup different tabs for different purposes.
    tab_expense_tracker, tab_life_saver = st.tabs(['Expense Tracker','Life Saver'])
    # ----------------------------------------------------------- Expense Tracker ------------------------------------------------------------------------------------
    with tab_expense_tracker:
        # setup tabs
        tab_add_update, tab_analytics, tab_reset = st.tabs(['Add/Update', 'Analytics', 'Reset'])

        # Add/Update Tab: Add or update database with expenses incurred.
        with tab_add_update:
            add_update()

        # Analytics Tab: Data displays category-wise expenses between the dates chosen.
        with tab_analytics:
            get_analytics()

        # Reset Tab: This resets the database for the user i.e. removes all entries.
        with tab_reset:
            reset()
    #----------------------------------------------------------------------- CHAT BOT SETUP ------------------------------------------------------------------------------
    # Add Chatbot to sidebar
    with st.sidebar:
        st.header("_Expensi_ 🤖")
        create_perplexity_clone()




