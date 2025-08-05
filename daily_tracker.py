#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 17:38:39 2025
streamlit-tracker-bot@tracker-app-467707.iam.gserviceaccount.com

@author: shyamdk
"""
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# === SHEET CONFIGURATION ===
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ah_-_4cDJx-jKgBbSKBroyesnInBPxi0ow-dssnFVRg/edit#gid=0"

# === AUTHORIZATION ===
@st.cache_resource
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

# === WORKSHEET ACCESS ===
@st.cache_resource
def get_daily_tracker_sheet():
    gc = authorize_gspread()
    sheet = gc.open_by_url(SHEET_URL)
    return sheet.worksheet("Sheet1")  # rename if your sheet is not Sheet1

worksheet = get_daily_tracker_sheet()

# === SECTION: DASHBOARD ===
def daily_dashboard():
    st.subheader("📊 Daily Tracker Dashboard")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        df['DATE'] = pd.to_datetime(df['DATE'])
        st.dataframe(df)
        st.write("Total Entries:", len(df))
    else:
        st.info("No entries found.")

# === SECTION: ADD ENTRY ===
def add_entry():
    st.subheader("➕ Add Entry")
    with st.form("add_form"):
        date_val = st.date_input("Date", value=date.today())
        param = st.text_input("Parameter")
        value = st.text_input("Value")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add")
        if submitted:
            worksheet.append_row([str(date_val), param, value, notes])
            st.success("Entry added successfully!")

# === SECTION: UPDATE ENTRY ===
def update_entry():
    st.subheader("✏️ Update Entry")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    if df.empty:
        st.info("No entries to update.")
        return

    row_to_edit = st.selectbox("Select entry to update", df.index)
    selected_row = df.iloc[row_to_edit]

    with st.form("update_form"):
        date_val = st.date_input("Date", value=pd.to_datetime(selected_row['DATE']).date())
        param = st.text_input("Parameter", value=selected_row['PARAMETER'])
        value = st.text_input("Value", value=selected_row['VALUE'])
        notes = st.text_area("Notes", value=selected_row['NOTES'])
        submitted = st.form_submit_button("Update")

        if submitted:
            worksheet.update(f"A{row_to_edit+2}", [[str(date_val), param, value, notes]])
            st.success("Entry updated successfully!")

# === SECTION: DELETE ENTRY ===
def delete_entry():
    st.subheader("🗑️ Delete Entry")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    if df.empty:
        st.info("No entries to delete.")
        return

    row_to_delete = st.selectbox("Select entry to delete", df.index)
    selected_row = df.iloc[row_to_delete]
    st.write(selected_row)

    if st.button("Delete"):
        worksheet.delete_rows(row_to_delete + 2)
        st.success("Entry deleted successfully!")
