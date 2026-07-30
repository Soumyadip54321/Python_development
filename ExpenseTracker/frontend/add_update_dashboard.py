import requests
import streamlit as st
import datetime as dt
import time
from ExpenseTracker.frontend.auth_dashboard import get_auth_headers

from sqlalchemy import false

category_types = ['Entertainment','Shopping','Food','Other','Rent','Electronics','Groceries']
API_url = 'http://127.0.0.1:8000'

@st.dialog("Delete expenses")
def delete_expenses(date : dt.date):
    '''
    Function to delete expenses permanently for a date.
    :param expenses:
    :return:
    '''
    st.warning("⚠️ This will permanently delete all expenses for this date. Do you intend to proceed?")
    left,col1,col2,right = st.columns([1,3,3,1])

    with col1:
        if st.button("Delete expense"):
            delete_response = requests.delete(f"{API_url}/delete_expenses/{date}", headers=get_auth_headers())
            if delete_response.status_code == 200:
                st.badge(f"{delete_response.json()['message']}", color='green', icon=":material/check:")
            else:
                st.error('Failed to delete')
            st.session_state.data_loaded = False
            time.sleep(5)
            st.rerun()

    with col2:
        if st.button("Cancel"):
            st.session_state.data_loaded = False
            st.rerun()

def add_update():
    '''
    UI Function to display expense tracker dashboard on Simpex.
    :return:
    '''

    date = st.date_input("Expense date to populate data for", value=dt.date.today(), format='YYYY/MM/DD')
    fetch_data = st.button('Fetch Data', type='primary')

    if fetch_data or st.session_state.data_loaded:
        # set session state to true so on re-run values populated remains and get updated to the database.
        st.session_state.data_loaded = True

        # make API call to fetch data for date chosen if available
        response = requests.get(f'{API_url}/add_update_expenses/{date}', headers=get_auth_headers())
        if response.status_code == 200:
            existing_expenses = response.json()
        else:
            st.warning(f'Failed to fetch data. No data available for {date}. Please add expenses below first.')
            existing_expenses = []

        # st.write(existing_expenses)

        # setup container to display and/or input data.
        with st.form("expense_form", enter_to_submit=False, clear_on_submit=False):

            # Create header row first
            header_col1, header_col2, header_col3 = st.columns(3)
            with header_col1:
                st.text("Amount", help='Expense incurred')
            with header_col2:
                st.text("Category", help='Expense category')
            with header_col3:
                st.text("Notes", help='Short description of the expense')

            # Stores all expenses incurred on the date
            expenses_on_date = []

            for i in range(10):

                # display data fetched from database
                if i < len(existing_expenses):
                    amount = float(existing_expenses[i]['amount'])
                    notes = existing_expenses[i]['notes']
                    category = existing_expenses[i]['category']

                    # in case of new category it is updated in category types.
                    if category not in category_types and category is not None:
                        category_types.append(category)
                else:
                    amount = 0.0
                    notes = ""
                    category = category_types[0]

                # pick values basis date and index location and display
                col1, col2, col3 = st.columns(3)

                with col1:
                    amount = st.number_input("amount", step=1.0, value=amount, key=f'amount_{date}_{i}',
                                             label_visibility='collapsed')
                with col2:
                    category = st.selectbox("category", category_types, index=category_types.index(category),
                                            key=f'category_{date}_{i}', label_visibility='collapsed',
                                            accept_new_options=True)
                with col3:
                    notes = st.text_input("notes", value=notes, key=f'notes_{date}_{i}',
                                          label_visibility='collapsed')

                # update expenses if amount > 0
                if(amount > 0.0):
                    expenses_on_date.append({
                        'amount': amount,
                        'category': category,
                        'notes': notes,
                    })

            # prepare data for database update
            user_expense_info = {'expenses': expenses_on_date}

            update_data = st.form_submit_button('Save', type='primary')
            delete_data = st.form_submit_button('Delete', type='secondary')
            # st.write(user_expense_info)

            # update expense data in the database for a specific date
            if update_data:
                # submit filtered expenses to database using API
                put_response = requests.put(f"{API_url}/expenses/{date}", json=user_expense_info, headers=get_auth_headers())
                if put_response.status_code == 200:
                    st.badge("Success: data saved.", color='green', icon=":material/check:")
                else:
                    st.error('Failed to post')
                st.session_state.data_loaded = False
                time.sleep(5)
                st.rerun()

            # remove expense data from the database corresponding to a date. On clicking it opens a dialog box to re-confirm deletion before proceeding.
            if delete_data:
                delete_expenses(date)