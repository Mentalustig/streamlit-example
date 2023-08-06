import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Read in data from the Google Sheet.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(csv_url)
    df['Week'] = pd.to_datetime(df['Week'])
    return df

# Constants
GOAL = 800000

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
    'Category': ['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others'],
    'Last Period': last_period_data,
    'Current Period': current_data
})
st.bar_chart(stacked_bar_chart_data.set_index('Category'))

# Calculate the difference between current and last period's sum
current_sum = current_data.sum()
last_period_sum = last_period_data.sum()
difference = current_sum - last_period_sum

# Success message and balloons
if difference >= 2000:
    st.success(f"Congratulations! This month's money is {difference} more than last month's sum.")
    st.balloons()

# Inputs (at the end)
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 5)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6) / 100
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2) / 100
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4) / 100

# Forecast calculation
forecasted_sum = current_data.sum() \
                + current_data['House Dellach'] * (1 + house_dellach_interest_rate) ** years_forecast \
                + current_data['Investment Account'] * (1 + investment_interest_rate) ** years_forecast \
                + monthly_investment_forecast * 12 * (1 + investment_interest_rate) ** years_forecast \
                + current_data['Savings Account'] * (1 + savings_account_interest_rate) ** years_forecast

st.write(f"Forecasted Sum: {forecasted_sum}")

# Footnote with assumptions and current goal
st.markdown("---")
st.markdown("**Assumptions and Current Goal:**")
st.markdown("The current goal is set at $800,000. This amount is based on the estimated monthly living expenses of $3,500 to $4,500. The forecast and visualizations above are built on the assumptions provided through the sliders, reflecting potential investment returns, interest rates, and other financial factors.")
