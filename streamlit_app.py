import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Read in data from the Google Sheet.
@st.cache(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(csv_url)
    df['Week'] = pd.to_datetime(df['Week'])
    return df

# Constants
GOAL = 800000
years_forecast = 10

# Load data
df = load_data(st.secrets["public_gsheets_url"])

# Dashboard Title
st.title("Mamis Finance Dashboard")
st.markdown("[Go to Google Sheet](https://docs.google.com/spreadsheets/d/1MGyZNI0FjOSYc3SEh3ZTAcjPtipjNU_AAdtqUWzdBsU/edit#gid=0)")

# Calculate current and last period's sum for each category
current_data = df.iloc[-1][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sort_values()
last_period_data = df.iloc[-2][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sort_values() if len(df) > 1 else [0] * 6

# Stacked Bar chart for current vs last period
stacked_bar_chart_data = pd.DataFrame({
    'Category': current_data.index,
    'Last Period': last_period_data,
    'Current Period': current_data
})
st.bar_chart(stacked_bar_chart_data.set_index('Category'))

# Success message and balloons
difference = current_data.sum() - last_period_data.sum()
if difference >= 2000:
    st.success(f"Congratulations! This month's money is {difference:.2f} more than last month's sum.")
    st.balloons()

# Forecast calculation for each category
forecasted_data = current_data.copy()
forecasted_data['House Dellach'] *= (1 + house_dellach_interest_rate / 100) ** years_forecast
forecasted_data['Investment Account'] *= (1 + investment_interest_rate / 100) ** years_forecast
forecasted_data['Investment Account'] += monthly_investment_forecast * 12 * (1 + investment_interest_rate / 100) ** years_forecast
forecasted_data['Savings Account'] *= (1 + savings_account_interest_rate / 100) ** years_forecast

# Create a new DataFrame row with forecasted data
forecasted_df = forecasted_data.to_frame().T
forecasted_df['Week'] = df.iloc[-1]['Week'] + pd.DateOffset(years=years_forecast)

# Append forecasted row to the DataFrame
df = pd.concat([df, forecasted_df], ignore_index=True)

# Stacked Area Chart
st.area_chart(df.set_index('Week')[['Inheritance', 'House Dellach', 'Bank Account', 'Savings Account', 'Investment Account', 'Others']])

# Donut chart for current goal progress
fig1 = px.pie(values=[current_data.sum(), GOAL - current_data.sum()], names=['Current', 'Remaining'], hole=0.3, title=f"Current Year ({datetime.now().year})")
fig1.update_traces(textinfo='percent+label', marker=dict(colors=['#1f77b4', '#ff7f0e']))

# Donut chart for forecasted goal progress
fig2 = px.pie(values=[forecasted_data.sum(), GOAL - forecasted_data.sum()], names=['Forecasted', 'Remaining'], hole=0.3, title=f"Forecasted Year ({datetime.now().year + years_forecast})")
fig2.update_traces(textinfo='percent+label', marker=dict(colors=['#1f77b4', '#ff7f0e']))

st.plotly_chart(fig1)
st.plotly_chart(fig2)

# Inputs (at the end)
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 10)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Print data as a table (at the bottom)
st.write(df)

# Footnote with assumptions and current goal
st.markdown("---")
st.markdown("**Assumptions and Current Goal:**")
st.markdown("The current goal is set at $800,000. This amount is based on the estimated monthly living expenses of $3,500 to $4,500. The forecast and visualizations above are built on the assumptions provided through the sliders, reflecting potential investment returns, interest rates, and other financial factors.")
