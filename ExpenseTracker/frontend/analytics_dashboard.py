import streamlit as st
import requests
import datetime as dt
import pandas as pd
import plotly.express as px

API_url = 'http://127.0.0.1:8000'

def get_analytics():
    '''
    Function that displays UI under analytics tab in Simpex dashboard.
    :return:
    '''
    dates_for_expense_fetch = {}

    # display date fields
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            date1 = st.date_input("Start Date", value=dt.date.today(), format='YYYY/MM/DD')
        with col2:
            date2 = st.date_input("End Date", value=dt.date.today() + dt.timedelta(7), format='YYYY/MM/DD')

        dates_for_expense_fetch.update({
            'start': date1.isoformat(),
            'end': date2.isoformat(),
        })

        submitted = st.button('Get Analytics', type='primary')

        # fetch data from server and display
        if submitted:
            response = requests.post(f'{API_url}/analytics/', json=dates_for_expense_fetch)
            if response.status_code == 200:
                expenses_category_wise = response.json()

                # In case of no data in database to fetch
                if "message" in expenses_category_wise:
                    st.write(expenses_category_wise['message'])
                else:
                    df = pd.DataFrame(expenses_category_wise)

                    # display barchart & pie-chart
                    with st.container(border=True):
                        fig_bar = px.bar(df, x='category', y='total', color='category',
                                         title='Expenses across categories')
                        st.plotly_chart(fig_bar)
                        fig = px.pie(df, names='category', values='total',
                                     title='%-wise distribution of expenses across categories')
                        st.plotly_chart(fig)
            else:
                st.error('Sorry. Couldn\'t connect. Try again!!')