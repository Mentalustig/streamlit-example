import pandas as pd
import streamlit as st
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

# Find current and last period data
current_data = df.iloc[-1][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']]
last_period_data = df.iloc[-2][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']] if len(df) > 1 else [0] * 6

# Combine current and last period data for the grouped bar chart
bar_chart_data = pd.DataFrame({
    'Category': current_data.index,
    'This Period': current_data.values,
    'Last Period': last_period_data.values
})

# Plot the grouped bar chart
fig = go.Figure(data=[
    go.Bar(name='This Period', x=bar_chart_data['Category'], y=bar_chart_data['This Period']),
    go.Bar(name='Last Period', x=bar_chart_data['Category'], y=bar_chart_data['Last Period'])
])
fig.update_layout(barmode='group')
st.plotly_chart(fig)

# Success message and balloons
total_difference = current_data.sum() - last_period_data.sum()
if total_difference >= 2000:
    st.success(f"Congratulations! This month's money is {total_difference} more than last month's sum.")
    st.balloons()

# Inputs (at the end)
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 10)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Forecasted data
forecasted_data = df.iloc[-1].copy()
for year in range(1, years_forecast + 1):
    forecasted_data['Investment Account'] *= (1 + investment_interest_rate / 100)
    forecasted_data['House Dellach'] *= (1 + house_dellach_interest_rate / 100)
    forecasted_data['Savings Account'] *= (1 + savings_account_interest_rate / 100)
    forecasted_data['Investment Account'] += monthly_investment_forecast * 12 * ((1 + (investment_interest_rate / 100 / 12)) ** (12 * year) - 1)
    forecasted_row = df.iloc[-1].copy()
    forecasted_row['Week'] += pd.DateOffset(years=year)
    forecasted_row[['Bank Account', 'Investment Account', 'House Dellach', 'Savings Account']] = forecasted_data[['Bank Account', 'Investment Account', 'House Dellach', 'Savings Account']]
    df = pd.concat([df, forecasted_row], ignore_index=True)

# Define the order of categories for the stacked area chart
order_of_categories = ['Inheritance', 'Bank Account', 'Others', 'Savings Account', 'House Dellach', 'Investment Account']

# Plot the stacked area chart with the specified order
st.area_chart(df.set_index('Week')[order_of_categories])

# Current Year Donut
current_year_donut = go.Figure(data=[go.Pie(values=[current_data.sum(), GOAL - current_data.sum()], labels=['Current', 'Remaining'], hole=.3)])
current_year_donut.update_layout(title_text="Current Year")

# Forecasted Year Donut
forecasted_year_donut = go.Figure(data=[go.Pie(values=[forecasted_data['Total'].sum(), GOAL - forecasted_data['Total'].sum()], labels=['Forecasted', 'Remaining'], hole=.3)])
forecasted_year_donut.update_layout(title_text="Forecasted Year")

# Display donuts side by side
col1, col2 = st.columns(2)
col1.plotly_chart(current_year_donut)
col2.plotly_chart(forecasted_year_donut)

# Print data as a table (at the bottom)
st.write(df)

# Footnote with assumptions and current goal
st.markdown("---")
st.markdown("**Assumptions and Current Goal:**")
st.markdown("The current goal is set at $800,000. This amount is based on the estimated monthly living expenses of $3,500 to $4,500. The forecast and visualizations above are built on the assumptions provided through the sliders, reflecting potential investment returns, interest rates, and other financial factors.")
