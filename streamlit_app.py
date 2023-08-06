import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
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

# Calculate current and last period's sum
current_sum = df.iloc[-1][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum()
last_period_sum = df.iloc[-2][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum() if len(df) > 1 else 0

# Success message and balloons
if current_sum - last_period_sum >= 2000:
    st.success("Congratulations! This month's money is at least 2000 more than last month's sum.")
    st.balloons()

# Inputs
years_forecast = st.slider("Number of Years for Forecast", 1, 30, 5)
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 2000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Calculate current and forecasted sum
current_sum = df.iloc[-1][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum()
forecasted_sum = current_sum

# Stacked Area Chart
df['Total'] = df[['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum(axis=1)
df['Forecast'] = df['Total']

for i in range(12 * years_forecast): # Forecast for the number of years
    forecasted_sum += monthly_investment_forecast
    forecasted_sum *= (1 + (investment_interest_rate + house_dellach_interest_rate + savings_account_interest_rate) / 100 / 12)
    next_date = df.iloc[-1]['Week'] + pd.DateOffset(months=1)
    new_row = {'Week': next_date, 'Forecast': forecasted_sum}
    df = df.append(new_row, ignore_index=True)

df['Goal'] = GOAL

plt.figure(figsize=(10, 6))
plt.fill_between(df['Week'], df['Total'], label='Total', alpha=0.5)
plt.fill_between(df['Week'], df['Forecast'], label='Forecast', alpha=0.5)
plt.plot(df['Week'], df['Goal'], label='Goal', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Amount')
plt.legend()
plt.title('Financial Progress and Forecast')
st.pyplot()

# Donut chart for current goal progress
fig1, ax1 = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
data1 = [current_sum, GOAL - current_sum]
labels1 = [f'Current {current_sum / GOAL * 100:.1f}%', 'Remaining']
wedges1, texts1, autotexts1 = ax1.pie(data1, autopct='%1.1f%%', textprops=dict(color="w"), startangle=90, wedgeprops=dict(width=0.3))
ax1.legend(wedges1, labels1, title="Current Goal Progress", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.setp(autotexts1, size=10, weight="bold")
st.pyplot(fig1)

# Donut chart for forecasted goal progress
fig2, ax2 = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
data2 = [forecasted_sum, GOAL - forecasted_sum]
labels2 = [f'Forecasted {forecasted_sum / GOAL * 100:.1f}%', 'Remaining']
wedges2, texts2, autotexts2 = ax2.pie(data2, autopct='%1.1f%%', textprops=dict(color="w"), startangle=90, wedgeprops=dict(width=0.3))
ax2.legend(wedges2, labels2, title="Forecasted Goal Progress", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.setp(autotexts2, size=10, weight="bold")
st.pyplot(fig2)


