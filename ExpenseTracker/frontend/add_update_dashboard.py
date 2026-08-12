from math import ceil

import pandas as pd
import requests
import streamlit as st
import datetime as dt
import time
from ExpenseTracker.frontend.auth_dashboard import get_auth_headers

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
            delete_response = requests.delete(f"{API_url}/expenses/delete/{date}", headers=get_auth_headers())
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

def create_dataframe_of_expenses(existing_expenses, rows_per_page):
    '''
    Function to create dataframe from expenses fetched for a user with provision to add new expenses.
    :param existing_expenses:
    :return:
    '''
    if existing_expenses:
        df = pd.DataFrame(existing_expenses)
    else:
        df = pd.DataFrame()

    extra_rows = len(df) % rows_per_page
    rows_to_be_added_to_form_a_page = rows_per_page - extra_rows if extra_rows else rows_per_page

    # pad dataframe with 10 more entries
    df_empty = pd.DataFrame(
        [
            {
                'amount': 0.0,
                'category': None,
                'notes': "",
            }
            for i in range(rows_to_be_added_to_form_a_page)
        ]
    )
    df = pd.concat([df, df_empty], axis=0, ignore_index=True)
    return df

def fetch_user_data(num_total_rows,date):
    '''
    Function to fetch all user expenses populated in the form across all pages.
    :param num_total_rows:
    :return:
    '''

    ans = []

    for idx in range(num_total_rows):
        amt_key = f'amount_{date}_{idx}'
        cat_key = f'category_{date}_{idx}'
        notes_key = f'notes_{date}_{idx}'

        if amt_key in st.session_state and st.session_state[amt_key] > 0.0:
            ans.append({
                'amount': st.session_state[amt_key],
                'category': st.session_state[cat_key],
                'notes': st.session_state[notes_key],
            })

    return ans

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
        response = requests.get(f'{API_url}/expenses/add_update/{date}', headers=get_auth_headers())
        if response.status_code == 200:
            existing_expenses = response.json()
        else:
            st.warning(f'Failed to fetch data. No data available for {date}. Please add expenses below first.')
            existing_expenses = []

#-----------------------------------------------PAGINATION--------------------------------------------------------------------------
        # create a dataframe to capture all expenses with provision to add new expenses
        rows_per_page = 10
        df_expenses = create_dataframe_of_expenses(existing_expenses, rows_per_page)

        # define paging
        num_pages_needed = ceil(len(df_expenses) / rows_per_page)

        # reserve spot above pagination to display dataframe rows across various pages
        dataframe_spot = st.empty()

        # make a copy of category types
        category_types_copy = category_types

        with st.container(horizontal_alignment='center'):
            page = st.pagination(num_pages=num_pages_needed)

        # This start & end indices is recomputed as user navigates pages using pagination
        start_idx = (page-1) * rows_per_page
        end_idx = start_idx + rows_per_page

        # setup container to display dataframe with pagination at the bottom.
        with st.form("expense_form", enter_to_submit=False, clear_on_submit=False):

            # Create headers per page
            header_col1, header_col2, header_col3 = st.columns(3)
            with header_col1:
                st.text("Amount", help='Expense incurred')
            with header_col2:
                st.text("Category", help='Expense category')
            with header_col3:
                st.text("Notes", help='Short description of the expense')

            for idx in range(start_idx, end_idx):

                # display amount, category and notes data
                amount = df_expenses.loc[idx, 'amount']
                category = df_expenses.loc[idx, 'category']
                notes = df_expenses.loc[idx, 'notes']

                if category and category not in category_types_copy:
                    category_types_copy.append(category)

                # pick values basis date and index location and display
                col1, col2, col3 = st.columns(3)

                with col1:
                    amount = st.number_input("amount", step=1.0, value=amount, key=f'amount_{date}_{idx}',
                                             label_visibility='collapsed')
                with col2:
                    category = st.selectbox("category", category_types_copy,index=None if category is None else category_types_copy.index(category),
                                            key=f'category_{date}_{idx}', label_visibility='collapsed',
                                            accept_new_options=True)
                with col3:
                    notes = st.text_input("notes", value=notes, key=f'notes_{date}_{idx}',
                                          label_visibility='collapsed')

            update_data = st.form_submit_button('Save', type='primary')
            delete_data = st.form_submit_button('Delete', type='secondary')
            # st.write(user_expense_info)

            if update_data:
                # fetch user data to be uploaded on submission
                expenses_on_date = fetch_user_data(num_pages_needed*rows_per_page,date)
                user_expense_info = {'expenses': expenses_on_date}

                # submit filtered expenses to database using API
                put_response = requests.put(f"{API_url}/expenses/update/{date}", json=user_expense_info, headers=get_auth_headers())
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