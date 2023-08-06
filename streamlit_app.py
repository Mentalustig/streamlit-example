import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Read in data from the Google Sheet.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(csv_url)
    # Convert relevant columns to numeric
    for col in ['Investment Account', 'House Dellach', 'Bank Account', 'Savings Account']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# Constants
GOAL = 800000

# Load data
df = load_data(st.secrets["public_gsheets_url"])

# Convert 'Week' to datetime and extract the year
df['Week'] = pd.to_datetime(df['Week'])
df['Year'] = df['Week'].dt.year

# Current amounts
investment_amount = float(df.iloc[-1]['Investment Account'])
house_dellach = float(df.iloc[-1]['House Dellach'])
savings_account = float(df.iloc[-1]['Savings Account'])

# Dashboard Title
st.title("Mamis Finance Dashboard")
st.markdown("[Go to Google Sheet](https://docs.google.com/spreadsheets/d/1MGyZNI0FjOSYc3SEh3ZTAcjPtipjNU_AAdtqUWzdBsU/edit#gid=0)")

# Inputs
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 6000, 1000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Calculate current and forecasted sum
current_sum = investment_amount + house_dellach + savings_account
forecasted_sum = current_sum

# Stacked Area Chart
df['Total'] = df['Investment Account'] + df['House Dellach'] + df['Bank Account']
df['Forecast'] = df['Total']
for i in range(12): # 12 months forecast
    forecasted_sum += monthly_investment_forecast
    forecasted_sum *= (1 + (investment_interest_rate + house_dellach_interest_rate + savings_account_interest_rate) / 100 / 12)
    df.loc[df.index[-1] + 1, 'Forecast'] = forecasted_sum

df['Goal'] = GOAL

# Plotting the area chart
fig, ax = plt.subplots()
ax.stackplot(df['Year'], df['Total'], df['Forecast'], labels=['Total', 'Forecast'])
ax.plot(df['Year'], df['Goal'], label='Goal', color='red')
plt.legend(loc='upper left')
st.pyplot(fig)

# Success message and balloons
if forecasted_sum - current_sum >= 2000:
    st.success("Congratulations! This month's money is at least 2000 more than last month's sum.")
    st.balloons()

# ...

# Donut chart for current goal progress
fig1, ax1 = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
data1 = [current_sum / GOAL * 100, 100 - current_sum / GOAL * 100]
labels1 = ['Current %', 'Remaining %']
wedges1, texts1, autotexts1 = ax1.pie(data1, autopct='%1.1f%%', textprops=dict(color="w"), startangle=90, wedgeprops=dict(width=0.3))
ax1.legend(wedges1, labels1, title="Current Goal Progress", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.setp(autotexts1, size=10, weight="bold")
st.pyplot(fig1)

# Donut chart for forecasted goal progress
fig2, ax2 = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
data2 = [forecasted_sum / GOAL * 100, 100 - forecasted_sum / GOAL * 100]
labels2 = ['Forecasted %', 'Remaining %']
wedges2, texts2, autotexts2 = ax2.pie(data2, autopct='%1.1f%%', textprops=dict(color="w"), startangle=90, wedgeprops=dict(width=0.3))
ax2.legend(wedges2, labels2, title="Forecasted Goal Progress", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.setp(autotexts2, size=10, weight="bold")
st.pyplot(fig2)

# Print data as a table
st.write(df)
