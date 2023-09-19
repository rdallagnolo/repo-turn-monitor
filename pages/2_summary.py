# loading required libraries
import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

st.set_page_config(page_title="Line change monitor", page_icon=":bird:", layout="centered", initial_sidebar_state="auto", menu_items=None)

# defining relative path to folder

# folder_path = 'StreamlitApp/LineChanges' ## this is the path for the live page
folder_path = 'LineChanges/' ## this is the path for the local work

# Get a list of all CSV files in the folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Initialize an empty list to store the statistics dictionaries
summary_data = []

# Loop through each CSV file and calculate statistics
for file in csv_files:
    # Extract digits 13 and 14 from the file name
    line_change = file[12:14]
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(os.path.join(folder_path, file))
    
    # Convert the 'Unnamed: 0' column to datetime objects
    df['Unnamed: 0'] = pd.to_datetime(df['Unnamed: 0'])
    
    # Calculate turn duration
    lc_time = (df['Unnamed: 0'].iloc[-1] - df['Unnamed: 0'].iloc[0]).seconds / 3600
    lc_time = round(lc_time, 2)

    # Calculate distance travelled
    distances = np.sqrt((df['V1 Easting'] - df['V1 Easting'].shift())**2 + (df['V1 Northing'] - df['V1 Northing'].shift())**2)
    distances.iloc[0] = 0
    total_distance = distances.sum() / 1000
    total_distance = round(total_distance, 2)

    # Calculate average speed
    factor = 0.5399568
    average_speed = (total_distance / lc_time) * factor
    average_speed = round(average_speed,2)
    
    # Get the turn corner
    area = df['Area'].iloc[0]

    # Create a dictionary with the statistics
    stats_dict = {'Line Change': line_change, 
                  'Turn Duration (hours)': lc_time, 
                  'Distance Travelled (km)': total_distance, 
                  'Average Speed (knots)': average_speed,
                  'Area': area}
    
    # Append the statistics dictionary to the list
    summary_data.append(stats_dict)

# Convert the list of dictionaries to a DataFrame
summary_df = pd.DataFrame(summary_data)

# Sort the DataFrame by the 'Line Change' column
summary_df = summary_df.sort_values(by='Line Change')

# Reset the index
summary_df.reset_index(drop=True, inplace=True)

# Add a new column "extended" based on the condition
summary_df['extended'] = summary_df['Turn Duration (hours)'].apply(lambda x: 'yes' if x > 3.35 else 'no')

# Calculate the average for the numeric columns (excluding "Line Change") based on the "Area" column
averages = summary_df.groupby('Area').agg({'Turn Duration (hours)': 'mean', 'Distance Travelled (km)': 'mean', 'Average Speed (knots)': 'mean'}).reset_index()

# Count the number of observations for the "Line Change" column
count_observations = summary_df.groupby('Area')['Line Change'].count().reset_index()
count_observations.rename(columns={'Line Change': 'Line changes count'}, inplace=True)

# Merge the two DataFrames based on the "Area" column
result = pd.merge(averages, count_observations, on='Area')

# Rearrange the columns so that "Observations Count" appears after "Area" and renaming columns
result = result[['Area', 'Line changes count', 'Turn Duration (hours)', 'Distance Travelled (km)', 'Average Speed (knots)']]
result.columns = ['Area', 'LC count (n)', 'Average duration (hours)', 'Average distance (km)', 'Average speed (knots)']

# Downtime line change
n_lc = len(summary_df)
nominal_lc = n_lc * 3.35
total_lc = summary_df['Turn Duration (hours)'].sum()
delays = total_lc - nominal_lc

data = {
    'Nominal LC': [nominal_lc],
    'Total LC': [total_lc],
    'Downtime': [delays]
}

df = pd.DataFrame(data)


with st.expander('Downtime',expanded=True):
    st.table(df)


with st.expander('Averages by turn area', expanded=True):
    st.table(result)

with st.expander('Line change summary'):
    st.table(summary_df)


# ploting average speed by line in the 2 different turn areas

# average speed
fig1 = px.line(
summary_df,
x='Line Change',
y='Average Speed (knots)',
color='Area',
labels={'Line Change': 'Line Change', 'Average Speed (knots)': 'Average Speed'},
markers=True,
)

st.plotly_chart(fig1)

#distance_travelled:
fig2 = px.line(
summary_df,
x='Line Change',
y='Distance Travelled (km)',
color='Area',
labels={'Line Change': 'Line Change', 'Average distance (km)': 'Average distance'},
markers=True,
)
st.plotly_chart(fig2)

#line_change_duration:
fig3 = px.line(
summary_df,
x='Line Change',
y='Turn Duration (hours)',
color='Area',
labels={'Line Change': 'Line Change', 'Average Duration (hours)': 'Average duration'},
markers=True,
)
st.plotly_chart(fig3)