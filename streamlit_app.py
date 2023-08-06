import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt

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

stacked_bar_data = pd.DataFrame({
    'Period': ['Last Period', 'Current Period'],
    'Bank Account': [df.iloc[-2]['Bank Account'], df.iloc[-1]['Bank Account']],
    'Investment Account': [df.iloc[-2]['Investment Account'], df.iloc[-1]['Investment Account']],
    'Inheritance': [df.iloc[-2]['Inheritance'], df.iloc[-1]['Inheritance']],
    'House Dellach': [df.iloc[-2]['House Dellach'], df.iloc[-1]['House Dellach']],
    'Savings Account': [df.iloc[-2]['Savings Account'], df.iloc[-1]['Savings Account']],
    'Others': [df.iloc[-2]['Others'], df.iloc[-1]['Others']]
})

fig_stacked_bar = go.Figure(data=[
    go.Bar(name='Bank Account', x=stacked_bar_data['Period'], y=stacked_bar_data['Bank Account']),
    go.Bar(name='Investment Account', x=stacked_bar_data['Period'], y=stacked_bar_data['Investment Account']),
    go.Bar(name='Inheritance', x=stacked_bar_data['Period'], y=stacked_bar_data['Inheritance']),
    go.Bar(name='House Dellach', x=stacked_bar_data['Period'], y=stacked_bar_data['House Dellach']),
    go.Bar(name='Savings Account', x=stacked_bar_data['Period'], y=stacked_bar_data['Savings Account']),
    go.Bar(name='Others', x=stacked_bar_data['Period'], y=stacked_bar_data['Others']),
])

# Change the bar mode
fig_stacked_bar.update_layout(barmode='stack')

st.plotly_chart(fig_stacked_bar)


# Inputs (at the end)
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 10)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)


# Forecasted data for each year
forecasted_data = df.iloc[-1].copy()
for i in range(years_forecast):
    forecasted_data['Investment Account'] = forecasted_data['Investment Account'] * (1 + investment_interest_rate / 100) + monthly_investment_forecast * 12
    forecasted_data['House Dellach'] = forecasted_data['House Dellach'] * (1 + house_dellach_interest_rate / 100)
    forecasted_data['Savings Account'] = forecasted_data['Savings Account'] * (1 + savings_account_interest_rate / 100)
    forecasted_data['Week'] += pd.DateOffset(years=1)
    forecasted_data['Bank Account'] = forecasted_data['Bank Account']
    forecasted_data['Others'] = forecasted_data['Others']
    forecasted_data['Inheritance'] = forecasted_data['Inheritance']

    # Converting the forecasted_data Series to a DataFrame and concatenating it with the existing df
    forecasted_row_series = pd.Series(forecasted_data)
    df = pd.concat([df, forecasted_row_series.to_frame().T], ignore_index=True)


# Assuming 'Week' is in datetime format
df['Week'] = pd.to_datetime(df['Week'])

# Setting 'Week' as the index
df.set_index('Week', inplace=True)

# Plotting the stacked area chart
fig, ax = plt.subplots(figsize=(10, 6))
df.plot.area(ax=ax, alpha=0.4)
plt.title('Stacked Area Chart for Historical and Forecasted Data')
plt.xlabel('Time Period')
plt.ylabel('Value')
plt.legend(title='Categories', loc='center left', bbox_to_anchor=(1.0, 0.5))
plt.show()

# Assuming 'current_data' is the sum of all categories for the current year
current_data = df.iloc[-1].drop('Week').sum()
GOAL = 500000  # Set your goal here

# Current Year Donut
current_sum = current_data
current_remaining = GOAL - current_data
fig_donut_current = go.Figure(data=[go.Pie(values=[current_sum, current_remaining], labels=['Current', 'Remaining'], hole=.3)])
fig_donut_current.update_layout(title_text="Current Year")

# Forecasted Year Donut
# Assuming 'forecasted_data' is the last row of the forecast
forecasted_data = df.iloc[-1].drop('Week')
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
