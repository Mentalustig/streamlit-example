# streamlit_app.py

import pandas as pd
import streamlit as st

# Read in data from the Google Sheet.
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url, parse_dates=['Week'], thousands=',', decimal='.')

df = load_data(st.secrets["public_gsheets_url"])

# Print results.
for row in df.itertuples():
    st.write(f"{row.Week}: Bank Account = {row['Bank Account']}, Investment Account = {row['Investment Account']}, Inheritance = {row['Inheritance']}, House Dellach = {row['House Dellach']}, Others = {row['Others']}")
