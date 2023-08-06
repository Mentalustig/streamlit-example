import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
fig_stacked_bar = go.Figure(data=[
    go.Bar(name='Last Period', x=stacked_bar_chart_data['Category'], y=stacked_bar_chart_data['Last Period']),
    go.Bar(name='Current Period', x=stacked_bar_chart_data['Category'], y=stacked_bar_chart_data['Current Period'])
])
fig_stacked_bar.update_layout(barmode='stack', title='Comparison of Current and Last Period')
st.plotly_chart(fig_stacked_bar)

# Calculate current and last period's total sum
current_sum = current_data.sum()
last_period_sum = last_period_data.sum()

# Success message and balloons
difference = current_sum - last_period_sum
if difference >= 2000:
    st.success(f"Congratulations! This month's money is {difference} more than last month's sum.")
    st.balloons()

# Print data as a table
st.write(df)

# Stacked Area Chart
df['Total'] = df[['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum(axis=1)
fig_area_chart = px.area(df, x='Week', y='Total', title='Financial Progress')
fig_area_chart.update_yaxes(range=[0, 1000000])  # Set y-axis limit to 1 million
st.plotly_chart(fig_area_chart)

# Donut chart for current goal progress
fig1 = px.pie(values=[current_sum, GOAL - current_sum], names=['Current', 'Remaining'], hole=0.3)
fig1.update_layout(title='Current Goal Progress')
st.plotly_chart(fig1)

# Donut chart for forecasted goal progress (you can replace forecasted_sum with the actual forecasted value)
forecasted_sum = current_sum  # Replace with actual forecasted value
fig2 = px.pie(values=[forecasted_sum, GOAL - forecasted_sum], names=['Forecasted', 'Remaining'], hole=0.3)
fig2.update_layout(title='Forecasted Goal Progress')
st.plotly_chart(fig2)

# Inputs (at the end)
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 5)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Footnote with assumptions and current goal
st.markdown("---")
st.markdown("**Assumptions and Current Goal:**")
st.markdown("The current goal is set at $800,000. This amount is based on the estimated monthly living expenses of $3,500 to $4,500. The forecast and visualizations above are built on the assumptions provided through the sliders, reflecting potential investment returns, interest rates, and other financial factors.")
