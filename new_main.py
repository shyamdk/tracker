#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 17:37:49 2025

@author: shyamdk
"""
import streamlit as st
import daily_tracker
import task_tracker  # Make sure you have this file already

st.set_page_config(page_title="Daily + Task Tracker", layout="wide")

st.sidebar.title("📋 Navigation")
section = st.sidebar.radio("Go to", ["Daily Tracker", "Task Tracker"])

if section == "Daily Tracker":
    st.sidebar.markdown("### Daily Tracker Options")
    option = st.sidebar.radio("Choose function", ["Dashboard", "Add Entry", "Update Entry", "Delete Entry"])

    if option == "Dashboard":
        daily_tracker.daily_dashboard()
    elif option == "Add Entry":
        daily_tracker.add_entry()
    elif option == "Update Entry":
        daily_tracker.update_entry()
    elif option == "Delete Entry":
        daily_tracker.delete_entry()

elif section == "Task Tracker":
    task_tracker.task_tracker_ui()

