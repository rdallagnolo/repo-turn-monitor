# loading required libraries
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Line change monitor", page_icon=":bird:", layout="centered", initial_sidebar_state="auto", menu_items=None)


# this bit of code is to protect this page
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    
    # initialize a 2 columns daschboard
    col1, col2 = st.columns(2)

    # adding the merge code on col1
    with col1:

        st.header("Add next 24hrs")

        # defining relative path to folder
        #directory_path = 'StreamlitApp/24hrVesselPosition' ## this is the path for the live page
        directory_path = '24hrVesselPosition/' ## this is the path for the local work

        # Get a list of all filenames in the directory with the .csv extension
        csv_files = [filename for filename in os.listdir(directory_path) if filename.endswith('.csv')]
        csv_files.sort(reverse=True)

        # Create a Streamlit selectbox with the CSV filenames
        selected_csv_a = st.selectbox("Select file", csv_files, key="a")
        selected_csv_b = st.selectbox("Select file", csv_files, key="b")

        selected_csv_a = directory_path + selected_csv_a
        selected_csv_b = directory_path + selected_csv_b

        if st.button(label="merge files"):
                        
            # Read the first CSV file into a DataFrame
            df1 = pd.read_csv(selected_csv_a, skiprows=[1])
            
            # Read the second CSV file into a DataFrame, skipping the header (first row)
            df2 = pd.read_csv(selected_csv_b,skiprows=[1])
            
            # Concatenate the two DataFrames vertically (stack them on top of each other)
            combined_df = pd.concat([df1, df2])

            # Save the combined DataFrame to a new CSV file
            # combined_df.to_csv("../StreamlitApp/24hrVesselPosition/database.csv", index=False)
            combined_df.to_csv("24hrVesselPosition/database.csv", index=False)

    # adding the turn extractor code on col2
    with col2:

        st.header("Turn extractor")

        # Specify the directory path where your files are located
        #directory_path = '../StreamlitApp/24hrVesselPosition/'
        directory_path = '24hrVesselPosition/'

        start_time = st.text_input('End of line', '2023-08-31 10:12:00')
        end_time = st.text_input('Start of line', '2023-08-31 14:12:00')
        line_change_number = st.text_input('Line change number','0')

        line_directions = ['North','South']
        line_change_location = st.selectbox('Line change location',line_directions)

        if st.button(label="process turn"):

            # loading and formatting the raw file
            #df = pd.read_csv('../StreamlitApp/24hrVesselPosition/database.csv')
            df = pd.read_csv('24hrVesselPosition/database.csv')
            df["Unnamed: 0"] = pd.to_datetime(df["Unnamed: 0"], unit="s")

            # transform the time input into a timedelta object
            start_time_decoded = pd.to_datetime(start_time)
            end_time_decoded = pd.to_datetime(end_time)

            # filter the dataframe in between the time range
            filtered_df = df[(df['Unnamed: 0'] >= start_time) & (df['Unnamed: 0'] <= end_time)]

            # add the corner name
            filtered_df["Area"] = line_change_location

            # export the filtered dataframe to a separate database (folder called "turn-folder")
            # folder_path = '../StreamlitApp/LineChanges/'
            folder_path = 'LineChanges/'
            file_name = f"line-change-{line_change_number}.csv"
            full_file_path = folder_path + file_name
            filtered_df.to_csv(full_file_path,index=False)