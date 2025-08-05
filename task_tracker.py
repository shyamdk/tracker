#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 17:38:09 2025

@author: shyamdk
"""

import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Task Sheet URL
TASK_SHEET_URL = "https://docs.google.com/spreadsheets/d/1WyJvCbtQW2Ywpjkmmu0C4h-N4VEnyq6f3_nzdghKbX8/edit#gid=0"

def authorize_gspread():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("gspread_service_account.json", scope)
        return gspread.authorize(creds)

gc = authorize_gspread()



# Initialize or Get Task Sheet
def get_or_create_task_sheet():
    sheet = gc.open_by_url(TASK_SHEET_URL)
    try:
        task_ws = sheet.worksheet("task_tracker")
    except:
        task_ws = sheet.add_worksheet(title="task_tracker", rows="100", cols="10")
        task_ws.append_row([
            "ADD_DATE", "TASK", "TARGET_DATE", "TASK_STATUS", "TASK_CATEGORY", "TASK_TYPE", "COMMENTS"
        ])
    return task_ws

task_ws = get_or_create_task_sheet()

# Core Data Ops
def get_tasks():
    records = task_ws.get_all_records()
    return pd.DataFrame(records)

def add_task(entry):
    task_ws.append_row(entry)

def update_task(row_idx, updated_row):
    task_ws.update(f'A{row_idx}:G{row_idx}', [updated_row])

def delete_task(row_idx):
    task_ws.delete_rows(row_idx)

# UI Components
def task_tracker_ui():
    st.title("🗂️ Task Tracker")

    action = st.sidebar.radio("Action", ["📋 Dashboard", "➕ Add Task", "✏️ Modify Task", "❌ Delete Task"])

    df = get_tasks()

    if action == "📋 Dashboard":
        st.subheader("📊 Task Dashboard")
        if df.empty:
            st.info("No tasks available.")
        else:
            # Filter
            df = df[df["TASK_STATUS"].isin(["Pending", "In Progress"])]
            df = df.sort_values(by="TASK_TYPE")

            categories = df["TASK_CATEGORY"].unique()
            for category in categories:
                st.markdown(f"### 📌 {category}")
                st.dataframe(df[df["TASK_CATEGORY"] == category])

    elif action == "➕ Add Task":
        st.subheader("➕ Add New Task")
        with st.form("add_task_form"):
            add_date = st.date_input("Add Date", value=datetime.today())
            task = st.text_input("Task")
            target_date = st.date_input("Target Date", value=datetime.today())
            task_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
            task_category = st.selectbox("Category", ["Personal", "Office"])
            task_type = st.selectbox("Type", ["Urgent", "Important", "Urgent and Important"])
            comments = st.text_area("Comments")

            if st.form_submit_button("Add Task"):
                add_task([
                    add_date.strftime("%d-%m-%y"),
                    task,
                    target_date.strftime("%d-%m-%y"),
                    task_status,
                    task_category,
                    task_type,
                    comments
                ])
                st.success("✅ Task Added!")

    elif action == "✏️ Modify Task":
        st.subheader("✏️ Modify Task")
        if df.empty:
            st.info("No tasks to modify.")
        else:
            task_list = df["TASK"].tolist()
            selected_task = st.selectbox("Select Task to Edit", task_list)
            task_index = df.index[df["TASK"] == selected_task][0] + 2  # +2 due to header and 0-indexing

            row = df[df["TASK"] == selected_task].iloc[0]
            with st.form("edit_task_form"):
                task = st.text_input("Task", value=row["TASK"])
                add_date = st.date_input("Add Date", datetime.strptime(row["ADD_DATE"], "%d-%m-%y"))
                target_date = st.date_input("Target Date", datetime.strptime(row["TARGET_DATE"], "%d-%m-%y"))
                task_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(row["TASK_STATUS"]))
                task_category = st.selectbox("Category", ["Personal", "Office"], index=["Personal", "Office"].index(row["TASK_CATEGORY"]))
                task_type = st.selectbox("Type", ["Urgent", "Important", "Urgent and Important"], index=["Urgent", "Important", "Urgent and Important"].index(row["TASK_TYPE"]))
                comments = st.text_area("Comments", value=row["COMMENTS"])

                if st.form_submit_button("Update Task"):
                    update_task(task_index, [
                        add_date.strftime("%d-%m-%y"),
                        task,
                        target_date.strftime("%d-%m-%y"),
                        task_status,
                        task_category,
                        task_type,
                        comments
                    ])
                    st.success("✅ Task Updated!")

    elif action == "❌ Delete Task":
        st.subheader("❌ Delete Task")
        if df.empty:
            st.info("No tasks to delete.")
        else:
            task_list = df["TASK"].tolist()
            selected_task = st.selectbox("Select Task to Delete", task_list)
            task_index = df.index[df["TASK"] == selected_task][0] + 2

            if st.button("Delete Task"):
                delete_task(task_index)
                st.success("✅ Task Deleted!")
