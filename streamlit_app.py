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

# Calculate current and last period's sum for each category
current_data = df.iloc[-1][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sort_values()
last_period_data = df.iloc[-2][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sort_values() if len(df) > 1 else [0] * 6

# Transpose the data to have periods as columns and categories as rows
stacked_bar_chart_data = pd.DataFrame({
    'Category': current_data.index,
    'Last Period': last_period_data.values,
    'Current Period': current_data.values
}).set_index('Category').T

# Plot the stacked bar chart with the total and difference
fig = go.Figure()
fig.add_trace(go.Bar(x=stacked_bar_chart_data.columns, y=stacked_bar_chart_data.loc['Current Period'], name='Current Period'))
fig.add_trace(go.Bar(x=stacked_bar_chart_data.columns, y=stacked_bar_chart_data.loc['Last Period'], name='Last Period'))
fig.update_layout(barmode='stack', title_text="Current vs Last Period", xaxis_title="Category", yaxis_title="Amount")
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
forecasted_data = current_data.copy()
future_investment = monthly_investment_forecast * 12 * ((1 + (investment_interest_rate / 100 / 12)) ** (12 * years_forecast) - 1) / (investment_interest_rate / 100 / 12)
forecasted_data['Investment Account'] = (forecasted_data['Investment Account'] + future_investment) * (1 + investment_interest_rate / 100) ** years_forecast
forecasted_data['House Dellach'] *= (1 + house_dellach_interest_rate / 100) ** years_forecast
forecasted_data['Savings Account'] *= (1 + savings_account_interest_rate / 100) ** years_forecast

# Sort categories by the change in forecasted values
forecasted_change = (forecasted_data - current_data).sort_values()
order_of_categories = forecasted_change.index.tolist()

# Combine historic and forecasted data
forecasted_row = df.iloc[-1].copy()
forecasted_row['Week'] += pd.DateOffset(years=years_forecast)
forecasted_row[order_of_categories] = forecasted_data[order_of_categories]
df = pd.concat([df, forecasted_row], ignore_index=True)

# Plot the stacked area chart with the specified order
st.area_chart(df.set_index('Week')[order_of_categories])

# Current Year Donut
fig1 = go.Figure(data=[go.Pie(values=[current_data.sum(), GOAL - current_data.sum()], labels=['Current', 'Remaining'], hole=.3)])
fig1.update_layout(title_text="Current Year")

# Forecasted Year Donut
fig2 = go.Figure(data=[go.Pie(values=[forecasted_data.sum(), GOAL - forecasted_data.sum()], labels=['Forecasted', 'Remaining'], hole=.3)])
fig2.update_layout(title_text="Forecasted Year")

# Display donuts side by side
col1, col2 = st.columns(2)
col1.plotly_chart(fig1)
col2.plotly_chart(fig2)

# Print data as a table (at the bottom)
st.write(df)

# Footnote with assumptions and current goal
st.markdown("---")
st.markdown("**Assumptions and Current Goal:**")
st.markdown("The current goal is set at $800,000. This amount is based on the estimated monthly living expenses of $3,500 to $4,500. The forecast and visualizations above are built on the assumptions provided through the sliders, reflecting potential investment returns, interest rates, and other financial factors.")
