import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Constants
GOAL = 800000

# Read in data from the Google Sheet.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(csv_url)
    df['Week'] = pd.to_datetime(df['Week'])
    return df

# Load data
df = load_data(st.secrets["public_gsheets_url"])

# Dashboard Title
st.title("Mamis Finance Dashboard")
st.markdown("[Go to Google Sheet](https://docs.google.com/spreadsheets/d/1MGyZNI0FjOSYc3SEh3ZTAcjPtipjNU_AAdtqUWzdBsU/edit#gid=0)")

# Calculate current and last period's sum for each category
current_data = df.iloc[-1][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']]
last_period_data = df.iloc[-2][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']] if len(df) > 1 else [0] * 6

# Stacked Bar chart for current vs last period
stacked_bar_chart_data = pd.DataFrame({
    'Category': list(current_data.index),
    'Last Period': last_period_data.values,
    'Current Period': current_data.values
}).melt(id_vars='Category', var_name='Period', value_name='Amount')

fig_stacked_bar = px.bar(stacked_bar_chart_data, x='Period', y='Amount', color='Category', barmode='stack', title='Comparison of Last Period vs Current Period')
st.plotly_chart(fig_stacked_bar)

# Print data as a table
st.write(df)

# Inputs (at the end)
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 5)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Forecast calculations
current_sum = current_data.sum()
forecasted_sum = current_sum + \
                 current_data['House Dellach'] * (1 + house_dellach_interest_rate / 100) ** years_forecast + \
                 current_data['Investment Account'] * (1 + investment_interest_rate / 100) ** years_forecast + \
                 monthly_investment_forecast * 12 * (1 + investment_interest_rate / 100) ** years_forecast + \
                 current_data['Savings Account'] * (1 + savings_account_interest_rate / 100) ** years_forecast

# Donut Charts
fig_donut_current = px.pie(values=[current_sum, GOAL - current_sum], names=['Current', 'Remaining'], hole=0.3, title='Current Goal Progress')
st.plotly_chart(fig_donut_current)

fig_donut_forecast = px.pie(values=[forecasted_sum, GOAL - forecasted_sum], names=['Forecasted', 'Remaining'], hole=0.3, title='Forecasted Goal Progress')
st.plotly_chart(fig_donut_forecast)

# Footnote with assumptions and current goal
st.markdown("---")
st.markdown("**Assumptions and Current Goal:**")
st.markdown("The current goal is set at $800,000. This amount is based on the estimated monthly living expenses of $3,500 to $4,500. The forecast and visualizations above are built on the assumptions provided through the sliders, reflecting potential investment returns, interest rates, and other financial factors.")
