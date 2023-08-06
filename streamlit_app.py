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

# Calculate current and last period's sum for each category
current_data = df.iloc[-1][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum()
last_period_data = df.iloc[-2][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum()

# Dashboard Title
st.title("Mamis Finance Dashboard")
st.markdown("[Go to Google Sheet](https://docs.google.com/spreadsheets/d/1MGyZNI0FjOSYc3SEh3ZTAcjPtipjNU_AAdtqUWzdBsU/edit#gid=0)")

# Bar chart for current vs last period
bar_chart_data = pd.DataFrame({
    'Period': ['Last Period', 'Current Period'],
    'Total Money': [last_period_data, current_data]
})
fig = px.bar(bar_chart_data, x='Period', y='Total Money', labels={'Total Money': 'Total Money (Sum of all Categories)'}, barmode='group')
st.plotly_chart(fig)

# Success message and balloons
total_difference = current_data - last_period_data
if total_difference >= 2000:
    st.success(f"Congratulations! This month's money is {total_difference} more than last month's sum.")
    st.balloons()

# Stacked bar chart for current vs last period
stacked_bar_data = pd.DataFrame({
    'Category': ['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others'],
    'Last Period': df.iloc[-2][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']],
    'Current Period': df.iloc[-1][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']]
}).melt(id_vars=['Category'], var_name='Period', value_name='Value')

fig_stacked_bar = px.bar(stacked_bar_data, x='Category', y='Value', color='Period', barmode='stack')
st.plotly_chart(fig_stacked_bar)


# Inputs (at the end)
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 10)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Forecasted data
forecasted_data = current_data.copy()
forecasted_data['Investment Account'] = forecasted_data['Investment Account'] * (1 + investment_interest_rate / 100 / 12) + monthly_investment_forecast * 12
forecasted_data['House Dellach'] = forecasted_data['House Dellach'] * (1 + house_dellach_interest_rate / 100 / 12)
forecasted_data['Savings Account'] = forecasted_data['Savings Account'] * (1 + savings_account_interest_rate / 100 / 12)

# Stacked Area Chart
df['Total'] = df[['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum(axis=1)
forecasted_row = df.iloc[-1].copy()
forecasted_row['Week'] += pd.DateOffset(years=years_forecast)
forecasted_row[['Bank Account', 'Investment Account', 'House Dellach', 'Savings Account']] = forecasted_data[['Bank Account', 'Investment Account', 'House Dellach', 'Savings Account']]
forecasted_row['Total'] = forecasted_data.sum()
df = df.append(forecasted_row, ignore_index=True)

# Assign colors to historical and forecast data
df['Type'] = ['Historical'] * len(df)
df.loc[df.index[-1], 'Type'] = 'Forecasted'

# Stacked Area Chart with historical and forecast data
fig_area = px.area(df, x='Week', y='Total', color='Type', line_group='Type', labels={'Total': 'Total Money (Sum of all Categories)'})
st.plotly_chart(fig_area)

# Current Year Donut
current_sum = current_data
current_remaining = GOAL - current_data
fig_donut_current = go.Figure(data=[go.Pie(values=[current_sum, current_remaining], labels=['Current', 'Remaining'], hole=.3)])
fig_donut_current.update_layout(title_text="Current Year")

# Forecasted Year Donut
forecasted_sum = forecasted_data.sum()
forecasted_remaining = GOAL - forecasted_data.sum()
fig_donut_forecasted = go.Figure(data=[go.Pie(values=[forecasted_sum, forecasted_remaining], labels=['Forecasted', 'Remaining'], hole=.3)])
fig_donut_forecasted.update_layout(title_text="Forecasted Year")

# Display donuts side by side
col1, col2 = st.columns(2)
col1.plotly_chart(fig_donut_current)
col2.plotly_chart(fig_donut_forecasted)

# Print data as a table (at the bottom)
st.write(df)

# Footnote with assumptions and current goal
st.markdown("---")
st.markdown("**Assumptions and Current Goal:**")
st.markdown("The current goal is set at $800,000. This amount is based on the estimated monthly living expenses of $3,500 to $4,500. The forecast and visualizations above are built on the assumptions provided through the sliders, reflecting potential investment returns, interest rates, and other financial factors.")
