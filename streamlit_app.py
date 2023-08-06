import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Read in data from the Google Sheet.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

df = load_data(st.secrets["public_gsheets_url"])

# Constants
GOAL = 800000

# Current amounts
investment_amount = float(df.iloc[-1]['Investment Account'])
house_dellach = float(df.iloc[-1]['House Dellach'])
savings_account = float(df.iloc[-1]['Bank Account'])

# Inputs
monthly_investment_forecast = st.slider("Monthly Investment Forecast", 0, 10000, 1000)
investment_interest_rate = st.slider("Investment Interest Rate (%)", 0, 10, 6)
house_dellach_interest_rate = st.slider("House Dellach Interest Rate (%)", 0, 10, 2)
savings_account_interest_rate = st.slider("Savings Account Interest Rate (%)", 0, 10, 4)

# Calculate current and forecasted sum
current_sum = investment_amount + house_dellach + savings_account
forecasted_sum = current_sum
for _ in range(12): # 12 months forecast
    forecasted_sum += monthly_investment_forecast
    forecasted_sum *= (1 + (investment_interest_rate + house_dellach_interest_rate + savings_account_interest_rate) / 100 / 12)

# Plotting
fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

data = [current_sum / GOAL * 100, forecasted_sum / GOAL * 100]
labels = ["Current %", "Forecasted %"]

wedges, texts, autotexts = ax.pie(data, autopct='%1.1f%%', textprops=dict(color="w"))

ax.legend(wedges, labels, title="Status", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

plt.setp(autotexts, size=10, weight="bold")

st.pyplot(fig)
