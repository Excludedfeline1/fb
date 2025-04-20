import base64
from email.policy import default
from typing import Optional

import streamlit as st
import pandas as pd
import time
import os

# Create a folder called data in the main project folder
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Define CSV file paths for each part of the usability testing
CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")


def save_to_csv(data_dict, csv_file):
    # Convert dict to DataFrame with a single row
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        # If CSV doesn't exist, write with headers
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        # Else, we need to append without writing the header!
        df_new.to_csv(csv_file, mode='a', header=False, index=False)


def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()


def main():
    st.title("Usability Testing Tool")

    home, consent, demographics, tasks, exit, report = st.tabs(
        ["Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"])

    with home:
        st.header("Introduction")
        st.write("""
        Welcome to the Usability Testing Tool for HCI. Today you will be testing my new Pokémon Team creation tool.
        Please take note that this tool relies on the opensource PokeAPI and may be subject to changes as the database also changes its information.
        Please be unbiased and report all findings honestly to better improve user experience.

        In this app, you will:
        1. Provide consent for data collection.
        2. Fill out a short demographic questionnaire.
        3. Perform a specific task (or tasks).
        4. Answer an exit questionnaire about your experience.
        5. View a summary report (for demonstration purposes).
        """)

    with consent:
        st.header("Consent Form")

        st.text("Please read the following consent form below and confirm your agreement:")
        st.write("**Consent Agreement**\n"
                    "- I understand the purpose of this usability study.\n"
                    "- I am aware that my data will be collected solely for research and improvement purposes. \n"
                    "- I can withdraw at any time.")
        consent_given = st.checkbox("I agree to the terms above")

        if st.button("Submit Consent"):
            if not consent_given:
                st.warning("You must agree to the consent terms before proceeding.")
            else:
                # Save the consent acceptance time
                st.success("Your consent has been recorded. Thank you!")
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "consent_given": consent_given
                }
                save_to_csv(data_dict, CONSENT_CSV)

    with demographics:
        st.header("Demographic Questionnaire")

        with st.form("demographic_form"):
            name = st.text_input("Name (Optional)",)
            age = st.number_input("Age", step=1, min_value=1)
            occupation = st.text_input("Occupation")
            familiarity = st.selectbox("How familiar are you with similar tools?", ["Not Familiar", "Somewhat Familiar", "Very Familiar"])
            submitted = st.form_submit_button("Submit Demographics")
            if submitted:
                if age < 18:
                    st.warning("You must be 18 or older to fill this form out.")
                elif not occupation:
                    st.warning("Please fill out the occupation field.")
                else:
                    data_dict = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "name": name,
                        "age": age,
                        "occupation": occupation,
                        "familiarity": familiarity
                    }
                    save_to_csv(data_dict, DEMOGRAPHIC_CSV)
                    st.success("Demographic data saved.")

    with tasks:
        st.header("Task Page")

        st.write("Please select a task and record your experience completing it.")

        # For this template, we assume there's only one task, in project 3, we will have to include the actual tasks
        selected_task = st.selectbox("Select Task", ["Task 1: Create a team of 6 Pokémon","Task 2: Attempt to edit your team by adding/removing Pokémon","Task 3: Use all features of the application without running into issues"])
        if selected_task =="Task 1: Create a team of 6 Pokémon":
            st.write("Task Description: Using the application, find and search for 6 different or same pokemon and create a full party of 6 Pokémon.")
        elif selected_task == "Task 2: Attempt to edit your team by adding/removing Pokémon":
            st.write(
                "Task Description: After creating a team of 6 Pokémon, attempt to clear the team either one by one or completely, and attempt to add a new Pokémon in its place.")
        else:
            st.write(
                "Task Description: Attempt to use all features built into the app. In this case try find a Pokémon with single or multiple forms, and play with all filtering options. Also open all tabs and navigate to all directories.")
        # Track success, completion time, etc.
        start_button = st.button("Start Task Timer")
        if start_button:
            st.session_state["start_time"] = time.time()
            st.info("Timer has started. Please complete your task and then click the 'Stop Task Timer' button to stop.")

        stop_button = st.button("Stop Task Timer")
        if stop_button and "start_time" in st.session_state:
            duration = time.time() - st.session_state["start_time"]
            st.success(f"Task completed in {duration: .2f} seconds!",)
            st.session_state["task_duration"] = duration

        success = st.radio("Was the task completed successfully?", ["Yes", "No", "Partial"])
        bugs = st.checkbox("Did you encounter any major bugs?")
        if bugs:
            traceback = st.text_area("Please copy paste the error message traceback here:")
            bug_desc = st.text_area("How did this bug occur?")
            bug_imp = st.slider("On a scale from 1 to 5, (1 being least concern, 5 being most concern) how much did this bug affect your experience?",step=1,min_value=1, max_value=5, value=3)

        notes = st.text_area("Observer Notes")

        if st.button("Save Task Results"):
            duration_val = st.session_state.get("task_duration", None)

            data_dict = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "task_name": selected_task,
                "success": success,
                "duration_seconds": duration_val if duration_val else "",
                "bug": traceback if bugs else "",
                "bug_description": bug_desc if bugs else "",
                "bug_impact": bug_imp if bugs else "",
                "notes": notes
            }
            save_to_csv(data_dict, TASK_CSV)
            st.success("Task data saved.")

            # Reset any stored time in session_state if you'd like
            if "start_time" in st.session_state:
                del st.session_state["start_time"]
            if "task_duration" in st.session_state:
                del st.session_state["task_duration"]

    with exit:
        st.header("Exit Questionnaire")

        with st.form("exit_form"):
            satisfaction = st.slider("Overall Satisfaction {1 = Very Low, 5 = Very High}",step=1, min_value=1, max_value=5,value=3)
            difficulty = st.slider("Overall Difficulty {1 = Very Easy, 5 = Very Hard}",step=1, min_value=1, max_value=5, value=3)
            open_feedback = st.text_area("Additional feedback or comments")
            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")
            if submitted_exit:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "satisfaction": satisfaction,
                    "difficulty": difficulty,
                    "open_feedback": open_feedback
                }
                save_to_csv(data_dict, EXIT_CSV)


                file_ = open("secret/124699-631359E2-3A45-42EA-A8D0-9BBE7331CFAE-0-1540677033.gif", "rb")
                contents = file_.read()
                data_url = base64.b64encode(contents).decode("utf-8")
                file_.close()
                st.success("Exit questionnaire data saved. (was feeling silly, pls dont mark me down for this T^T)")
                st.markdown(f'<img src="data:image/gif;base64,{data_url}" alt="Your GIF" width="200"> <img src="data:image/gif;base64,{data_url}" alt="Your GIF" width="200"> <img src="data:image/gif;base64,{data_url}" alt="Your GIF" width="200">',unsafe_allow_html=True)
                st.video("https://www.youtube.com/watch?v=NUYvbT6vTPs", autoplay=True, end_time=18)#34

    with report:
        st.header("Usability Report - Aggregated Results")

        st.write("**Consent Data**")
        consent_df = load_from_csv(CONSENT_CSV)
        if not consent_df.empty:
            st.dataframe(consent_df)
        else:
            st.info("No consent data available yet.")

        st.write("**Demographic Data**")
        demographic_df = load_from_csv(DEMOGRAPHIC_CSV)
        if not demographic_df.empty:
            st.dataframe(demographic_df)
        else:
            st.info("No demographic data available yet.")

        st.write("**Task Performance Data**")
        task_df = load_from_csv(TASK_CSV)
        if not task_df.empty:
            st.dataframe(task_df)
        else:
            st.info("No task data available yet.")

        st.write("**Exit Questionnaire Data**")
        exit_df = load_from_csv(EXIT_CSV)
        if not exit_df.empty:
            st.dataframe(exit_df)
        else:
            st.info("No exit questionnaire data available yet.")

        # Example of aggregated stats (for demonstration only)
        if not exit_df.empty:
            st.subheader("Exit Questionnaire Averages")
            avg_satisfaction = exit_df["satisfaction"].mean()
            avg_difficulty = exit_df["difficulty"].mean()
            st.write(f"**Average Satisfaction**: {avg_satisfaction:.2f}")
            st.write(f"**Average Difficulty**: {avg_difficulty:.2f}")


if __name__ == "__main__":
    main()