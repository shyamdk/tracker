#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 31 20:51:22 2025

@author: shyamdk
"""

# weight_tracker_app.py
import streamlit as st
import pandas as pd
from datetime import datetime

FILENAME = "63_day_weight_loss_tracker.csv"

# Load tracker
df = pd.read_csv(FILENAME)

# Sidebar
st.sidebar.title("📅 Select Day")
selected_day = st.sidebar.selectbox("Choose Day", df["Day"])

# Fetch row
row = df[df["Day"] == selected_day].index[0]
st.title(f"Update for {df.loc[row, 'Date']}")

# Input fields
weight = st.number_input("Weight (kg)", value=df.loc[row, "Weight (kg)"] or 0.0)
calories = st.number_input("Calories In", value=df.loc[row, "Calories In"] or 0)
activity = st.text_input("Activity (mins)", value=str(df.loc[row, "Activity (mins)"] or ""))
steps = st.number_input("Steps", value=df.loc[row, "Steps"] or 0)
water = st.number_input("Water (L)", value=df.loc[row, "Water (L)"] or 0.0)
mood = st.selectbox("Mood", ["🙂", "😐", "😕", "😣"], index=0)
notes = st.text_area("Notes", value=df.loc[row, "Notes"] or "")

# Save updates
if st.button("💾 Save Entry"):
    df.loc[row, "Weight (kg)"] = weight
    df.loc[row, "Calories In"] = calories
    df.loc[row, "Activity (mins)"] = activity
    df.loc[row, "Steps"] = steps
    df.loc[row, "Water (L)"] = water
    df.loc[row, "Mood"] = mood
    df.loc[row, "Notes"] = notes
    df.to_csv(FILENAME, index=False)
    st.success("Entry saved!")

# View all entries
if st.checkbox("📊 Show Tracker Table"):
    st.dataframe(df)
