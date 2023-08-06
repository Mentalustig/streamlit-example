import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Calculate the total difference
total_difference = current_data.sum() - last_period_data.sum()
st.markdown(f"### Total Difference Between Current and Last Period: ${total_difference:,.2f}")

# Stacked Bar chart for current vs last period
bar_chart_data = pd.DataFrame({
    'Period': ['Last Period', 'Current Period'],
    'Bank Account': [last_period_data['Bank Account'], current_data['Bank Account']],
    'Investment Account': [last_period_data['Investment Account'], current_data['Investment Account']],
    'Inheritance': [last_period_data['Inheritance'], current_data['Inheritance']],
    'House Dellach': [last_period_data['House Dellach'], current_data['House Dellach']],
    'Savings Account': [last_period_data['Savings Account'], current_data['Savings Account']],
    'Others': [last_period_data['Others'], current_data['Others']]
})
st.bar_chart(bar_chart_data.set_index('Period'))

# Print data as a table
st.write(df)

# Inputs (at the end)
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 10)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Forecast calculation
forecasted_sum = current_data.sum() + \
                 current_data['House Dellach'] * (1 + house_dellach_interest_rate / 100) ** years_forecast + \
                 current_data['Investment Account'] * (1 + investment_interest_rate / 100) ** years_forecast + \
                 monthly_investment_forecast * 12 * (1 + investment_interest_rate / 100) ** years_forecast + \
                 current_data['Savings Account'] * (1 + savings_account_interest_rate / 100) ** years_forecast

# Forecast calculation for each category
forecasted_data = current_data.copy()
forecasted_data['House Dellach'] *= (1 + house_dellach_interest_rate / 100) ** years_forecast
forecasted_data['Investment Account'] *= (1 + investment_interest_rate / 100) ** years_forecast
forecasted_data['Investment Account'] += monthly_investment_forecast * 12 * (1 + investment_interest_rate / 100) ** years_forecast
forecasted_data['Savings Account'] *= (1 + savings_account_interest_rate / 100) ** years_forecast

# Append forecasted data to the DataFrame
forecasted_row = forecasted_data.append(pd.Series({'Week': df.iloc[-1]['Week'] + pd.DateOffset(years=years_forecast)}))
df = df.append(forecasted_row, ignore_index=True)

# Stacked Area Chart
st.area_chart(df.set_index('Week')[['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']])

# ... (other code remains the same)
# Donut charts for current and forecasted goal progress
fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
fig.add_trace(go.Pie(labels=['Current', 'Remaining'], values=[current_data.sum(), GOAL - current_data.sum()], hole=.3), 1, 1)
fig.add_trace(go.Pie(labels=['Remaining', 'Forecasted'], values=[GOAL - forecasted_sum, forecasted_sum], hole=.3), 1, 2)
fig.update_traces(marker=dict(colors=['#636EFA', '#EF553B']))  # Set the same color for "Remaining" in both charts
st.plotly_chart(fig)

# Footnote with assumptions and current goal
st.markdown("---")
st.markdown("**Assumptions and Current Goal:**")
st.markdown("The current goal is set at $800,000. This amount is based on the estimated monthly living expenses of $3,500 to $4,500. The forecast and visualizations above are built on the assumptions provided through the sliders, reflecting potential investment returns, interest rates, and other financial factors.")
