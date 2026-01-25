import requests
import pandas as pd
import streamlit as st
import datetime as dt

category_types = ['Entertainment','Shopping','Food','Other','Rent','Electronics','Groceries']
API_url = 'http://127.0.0.1:8000'

def add_update():
    '''
    UI Function to display expense tracker dashboard on Simpex.
    :return:
    '''

    date = st.date_input("Expense date to populate data for", value=dt.date.today(), format='YYYY/MM/DD')
    fetch_data = st.button('Fetch Data', type='primary')

    if fetch_data:
        # make API call to fetch data for date chosen if available
        response = requests.get(f'{API_url}/expenses/{date}')
        if response.status_code == 200:
            existing_expenses = response.json()
        else:
            st.warning(f'Failed to fetch data. No data available for {date}. Please add expenses below first.')
            existing_expenses = []

        # setup container to display and/or input data.
        with st.form("expense_form", enter_to_submit=False, clear_on_submit=True):

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

                # update expenses
                expenses_on_date.append({
                    'amount': amount,
                    'category': category,
                    'notes': notes,
                })

            submitted = st.form_submit_button('Save', type='primary')
            if submitted:
                # filter expenses to contain only the entries with expenses incurred
                filtered_expenses = [expense for expense in expenses_on_date if expense['amount'] > 0.0]

                # submit filtered expenses to database using API
                post_response = requests.post(f"{API_url}/expenses/{date}", json=filtered_expenses)
                if post_response.status_code == 200:
                    st.badge("Success: data saved.", color='green', icon=":material/check:")
                else:
                    st.error('Failed to post')