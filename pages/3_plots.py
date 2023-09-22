# loading required libraries
import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

st.set_page_config(page_title="Line change monitor", page_icon=":bird:", layout="centered", initial_sidebar_state="auto", menu_items=None)

# defining folder relative path

# folder_path = 'StreamlitApp/LineChanges/' ## this is the path for the live page
folder_path = 'LineChanges/' ## this is the path for the local work

# Get a list of file names in the folder
file_names = os.listdir(folder_path)
file_names.sort(reverse=True)

# Filter the list to include only files (not directories)
file_names = [file for file in file_names if os.path.isfile(os.path.join(folder_path, file))]
# add a select box with the list of files
selected_turn = st.selectbox( "Select a turn", file_names)

# load the selected file as a data frame
full_file_path = folder_path + selected_turn
df = pd.read_csv(full_file_path)

# Convert the 'Unnamed: 0' column to datetime objects
df['Unnamed: 0'] = pd.to_datetime(df['Unnamed: 0'])

# calculate stats
   
# turn duration
lc_time = (df['Unnamed: 0'].iloc[-1] - df['Unnamed: 0'].iloc[0]).seconds / 3600
    
# distance travelled
distances = np.sqrt((df['V1 Easting'] - df['V1 Easting'].shift())**2 + (df['V1 Northing'] - df['V1 Northing'].shift())**2)
distances.iloc[0] = 0
total_distance = distances.sum() / 1000
    
# average speed
factor = 0.5399568
average_speed = (total_distance / lc_time) * factor

# speed distribution
df["V1 Bottom Speed"] = df["V1 Bottom Speed"] * 1.943844

# printing format
sot = df['Unnamed: 0'].iloc[-1]
sot = sot.strftime('%Y-%m-%d %H:%M:%S')

eot = df['Unnamed: 0'].iloc[0]
eot = eot.strftime('%Y-%m-%d %H:%M:%S')

st.write(f"Start of turn: {sot}")
st.write(f"End of turn: {eot}")

# build a scater plot with plotly express
fig = px.scatter(df, x='V1 Easting', y='V1 Northing')

fig.update_layout(
    width=600,
    height=600
)

# Add annotations for the statistics
annotations = [
    dict(x=0.5, y=0.6, xref='paper', yref='paper',
        text=f'Turn Duration: {lc_time:.2f} hours', 
        showarrow=False,font=dict(size=16)),
    dict(x=0.5, y=0.55, xref='paper', yref='paper',
        text=f'Distance Travelled: {total_distance:.2f} km', 
        showarrow=False,font=dict(size=16)),
    dict(x=0.5, y=0.50, xref='paper', yref='paper',
        text=f'Average Speed: {average_speed:.2f} knots', 
        showarrow=False,font=dict(size=16))
]

for annotation in annotations:
    fig.add_annotation(annotation)

# build a histogram of speeds with plotly express
fig2 = px.histogram(df["V1 Bottom Speed"], nbins=20)#, title='Bottom speed distribution (knots)')
fig2.update_xaxes(title_text='Bottom speed classes (knots)')
fig2.update_yaxes(title_text='Frequency (n)')
fig2.update_traces(marker_line_color='black', marker_line_width=1)
fig2.update_layout(showlegend=False)  # Remove the legend
#fig2.update_xaxes(range=[2, 6])

# Update the layout to set the width and height
fig2.update_layout(
    width=600,  # Set the width of the figure in pixels
    height=600,  # Set the height of the figure in pixels
    )
    
st.plotly_chart(fig)
st.plotly_chart(fig2)