import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Read in data from the Google Sheet.
@st.cache(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(csv_url)
    df['Week'] = pd.to_datetime(df['Week'])
    return df

# Constants
GOAL = 800000
COLOR_TURQUOISE = 'rgb(64, 224, 208)'
COLOR_LIGHT_TURQUOISE = 'rgb(224, 255, 255)'

# Load data
df = load_data(st.secrets["public_gsheets_url"])

# Dashboard Title
st.title("Mamis Finance Dashboard")
st.markdown("[Go to Google Sheet](https://docs.google.com/spreadsheets/d/1MGyZNI0FjOSYc3SEh3ZTAcjPtipjNU_AAdtqUWzdBsU/edit#gid=0)")

# Summary Section
st.header("Summary")
st.markdown("Welcome to your personal finance dashboard! Here you can see how well you're progressing toward your financial goals. The charts and numbers below show the current status and how things have changed since the last update. You can also explore forecasts for the future.")

# Guide Section
st.header("Guide")
st.markdown("This guide will help you understand the data and charts.")
with st.expander("How to Interpret the Data", expanded=False):
    st.markdown("""
    - **Bar Chart**: Compares total money for the current and last period.
    - **Stacked Bar Chart**: Breaks down the total money into different categories.
    - **Forecasted Year Donut**: Shows what you will own and what's remaining to reach your goal after a forecasted period.
    - **Current Year Donut**: Similar to Forecasted, but for the current year.
    - **Stacked Area Chart**: Represents how each category has evolved over time.
    """)

# Bar Chart Section
st.header("Bar Chart: Current vs Last Period")
current_data = df.iloc[-1][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum()
last_period_data = df.iloc[-2][['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']].sum()
fig = go.Figure()
fig.add_trace(go.Bar(x=['Current'], y=[current_data], name='Current'))
fig.add_trace(go.Bar(x=['Last Period'], y=[last_period_data], name='Last Period'))
fig.update_layout(height=300, showlegend=False, plot_bgcolor=COLOR_LIGHT_TURQUOISE)
st.plotly_chart(fig)

# Stacked Bar Chart
st.header("Stacked Bar Chart: Breakdown by Category")
categories = ['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Savings Account', 'Others']
fig_stacked_bar = px.bar(df, x='Week', y=categories, height=300, title='Stacked Bar Chart of Financial Categories')
fig_stacked_bar.update_layout(plot_bgcolor=COLOR_LIGHT_TURQUOISE)
st.plotly_chart(fig_stacked_bar)

# Donuts Section
st.header("Progress Towards Goal")
current_sum = df.iloc[-1][categories].sum()
forecasted_sum = current_sum * 1.05 # Assuming a 5% growth

fig_donut_current = go.Figure(data=[go.Pie(labels=['Owned', 'Remaining'], values=[current_sum, GOAL - current_sum], hole=.3)])
fig_donut_forecasted = go.Figure(data=[go.Pie(labels=['Forecasted', 'Remaining'], values=[forecasted_sum, GOAL - forecasted_sum], hole=.3)])

col1, col2 = st.columns(2)
col1.plotly_chart(fig_donut_current)
col2.plotly_chart(fig_donut_forecasted)

# Stacked Area Chart
st.header("Stacked Area Chart: Category Evolution")
fig_area = px.area(df, x='Week', y=categories, title='Evolution of Categories Over Time')
fig_area.update_layout(plot_bgcolor=COLOR_LIGHT_TURQUOISE)
st.plotly_chart(fig_area)

# Table of Latest Data
st.header("Latest Data")
st.write(df.tail())

# Footer Note
st.markdown("*Data is updated weekly. For any questions or concerns, please contact [support@email.com](mailto:support@email.com)*")
