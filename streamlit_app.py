# streamlit_app.py

import pandas as pd
import streamlit as st

# Title of the dashboard
st.title("Mamis Finance Dashboard")

# Button to direct to the Google Sheet
google_sheet_url = "https://docs.google.com/spreadsheets/d/1MGyZNI0FjOSYc3SEh3ZTAcjPtipjNU_AAdtqUWzdBsU/edit#gid=0"
if st.button("Open Google Sheet"):
    st.markdown(f'<a href="{google_sheet_url}" target="_blank">Click here to open the Google Sheet</a>', unsafe_allow_html=True)

# Read in data from the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

df = load_data(st.secrets["public_gsheets_url"])

# Print the entire DataFrame as a table.
st.table(df)
