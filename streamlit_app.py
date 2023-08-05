from collections import namedtuple
import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
import math


# Hardcoded data
data = {
    'Week': ['2023-01-01', '2023-05-08'],
    'Bank Account': [40000.0, 45000.0],
    'Investment Account': [np.nan, 2000.0],
    'Inheritance': [100000.0, 100000.0],
    'House Dellach': [200000.0, 200000.0],
    'Others': [5000.0, 5000.0]
}
df = pd.DataFrame(data)
df['Week'] = pd.to_datetime(df['Week'])

# User input for new data
def user_input_features():
    account_types = ['Bank Account', 'Investment Account', 'Inheritance', 'House Dellach', 'Others']
    account = st.selectbox('Account Type', account_types)
    amount = st.number_input('Amount', value=0.0)
    week = st.date_input('Week', value=datetime.now())
    return week, account, amount

# Calculate goal progress
def calculate_goal_progress(df, goal, interest_rate, years):
    # Exclude the 'Week' column when calculating the sum
    future_value = df.drop(columns=['Week']).sum().sum() * (1 + interest_rate)**years
    # Calculate progress towards goal
    goal_progress = future_value / goal
    return goal_progress

if st.button('Add Data'):
    week, account, amount = user_input_features()
    df.loc[df['Week'] == week, account] = amount

goal = st.number_input('Goal', value=0.0)
interest_rate = st.number_input('Annual Interest Rate', value=0.0)
years = st.number_input('Years', value=15)

goal_progress = calculate_goal_progress(df, goal, interest_rate, years)
st.write('Goal Progress: ', goal_progress)

# Plot stacked area chart using Altair
area_chart = alt.Chart(df.melt('Week', var_name='Account', value_name='Amount')).mark_area().encode(
    x='Week:T',
    y='Amount:Q',
    color='Account:N',
    tooltip=['Week', 'Account', 'Amount']
)
st.altair_chart(area_chart, use_container_width=True)

# Display data table
st.dataframe(df)

# Spiral plot
total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
num_turns = st.slider("Number of turns in spiral", 1, 100, 9)

Point = namedtuple('Point', 'x y')
spiral_data = []

points_per_turn = total_points / num_turns

for curr_point_num in range(total_points):
    curr_turn, i = divmod(curr_point_num, points_per_turn)
    angle = (curr_turn + 1) * 2 * math.pi * i / points_per_turn
    radius = curr_point_num / total_points
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    spiral_data.append(Point(x, y))

st.altair_chart(alt.Chart(pd.DataFrame(spiral_data), height=500, width=500)
    .mark_circle(color='#0068c9', opacity=0.5)
    .encode(x='x:Q', y='y:Q'))
