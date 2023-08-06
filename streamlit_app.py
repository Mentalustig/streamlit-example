# streamlit_app.py

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Title of the dashboard
st.title("Mamis Finance Dashboard")

# Hyperlink to direct to the Google Sheet
google_sheet_url = "https://docs.google.com/spreadsheets/d/1MGyZNI0FjOSYc3SEh3ZTAcjPtipjNU_AAdtqUWzdBsU/edit#gid=0"
st.markdown(f'[Open Google Sheet]({google_sheet_url})', unsafe_allow_html=True)

# Read in data from the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

df = load_data(st.secrets["public_gsheets_url"])

# Calculate the sum of money for the last two months
last_month_sum = df.iloc[-2, 1:].replace('-', '0').replace('€', '', regex=True).replace(',', '', regex=True).astype(float).sum()
this_month_sum = df.iloc[-1, 1:].replace('-', '0').replace('€', '', regex=True).replace(',', '', regex=True).astype(float).sum()

# Check if this month's sum is at least 2000 more than last month's sum
if this_month_sum - last_month_sum >= 2000:
    st.success("Great! This month's total is at least 2000 more than last month's total! 🎉")
    st.balloons()

# Print the entire DataFrame as a table.
st.table(df)

# Slider to adjust years towards the goal
years = st.slider('Years towards goal:', 1, 50, 10)

# Slider to adjust the expected interest rate
interest_rate = st.slider('Expected interest rate (%):', 1, 20, 5)

# Calculate the goal progress
investment_amount = float(df.iloc[-1]['Investment Account'])
goal_progress = investment_amount
for _ in range(years):
    goal_progress += goal_progress * (interest_rate / 100)

# Plot a doughnut chart to show the progress towards the goal
fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
data = [goal_progress, 1000000 - goal_progress] # Assuming the goal is 1,000,000
labels = ['Progress', 'Remaining']
wedges, texts, autotexts = ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3))
plt.legend(wedges, labels, title="Goal", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
plt.setp(autotexts, size=10, weight="bold")
st.pyplot(fig)
