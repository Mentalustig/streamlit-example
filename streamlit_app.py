import pandas as pd
import streamlit as st
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

# Print data as a table
st.write(df)

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

# Display the difference
difference = current_sum - last_period_sum
st.write(f"The difference between the current period and the last period is {difference:.2f}")

# Success message and balloons
if difference >= 2000:
    st.success("Congratulations! This month's money is at least 2000 more than last month's sum.")
    st.balloons()

# Stacked Area Chart
df['Total'] = df[['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum(axis=1)
df['Forecast'] = df['Total']
df['Goal'] = GOAL
st.area_chart(df.set_index('Week')[['Total', 'Forecast', 'Goal']])

# Inputs
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 5)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Calculate forecasted sum
forecasted_sum = current_sum
for i in range(12 * years_forecast): # Forecast for the number of years
    forecasted_sum += monthly_investment_forecast
    forecasted_sum *= (1 + (investment_interest_rate + house_dellach_interest_rate + savings_account_interest_rate) / 100 / 12)
    next_date = df.iloc[-1]['Week'] + pd.DateOffset(months=1)
    new_row = {'Week': [next_date], 'Forecast': [forecasted_sum]}
    new_row_df = pd.DataFrame(new_row)
    new_row_df = new_row_df.reindex(columns=df.columns)  # Align with the existing DataFrame columns
    df = pd.concat([df, new_row_df], ignore_index=True)

# Donut chart for current goal progress
st.pie_chart([current_sum, GOAL - current_sum], labels=[f'Current {current_sum / GOAL * 100:.1f}%', 'Remaining'])

# Donut chart for forecasted goal progress
st.pie_chart([forecasted_sum, GOAL - forecasted_sum], labels=[f'Forecasted {forecasted_sum / GOAL * 100:.1f}%', 'Remaining'])
