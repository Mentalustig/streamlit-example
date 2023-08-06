# streamlit_app.py

import pandas as pd
import streamlit as st

# Read in data from the Google Sheet.
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

df = load_data(st.secrets["public_gsheets_url"])

# Print the entire DataFrame as a table.
st.table(df)
