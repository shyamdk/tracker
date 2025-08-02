
'''
cd path/to/tracker-clean
git init

echo -e "*.pdf\n*.csv\nhelp.md" > .gitignore

git add wmanage-main.py
git commit -m "Initial commit: Added main Python app"

git remote remove origin
git remote add origin https://github.com/shyamdk/tracker.git

git push -u origin main

(if error)
git branch -M main
git push -u origin main


git add .
git commit -m "Prepare for Streamlit deployment"
git push origin main



echo "gspread_service_account.json" >> .gitignore


git rm --cached gspread_service_account.json
git commit -m "Remove secret"


git push origin main


mkdir -p .streamlit
touch .streamlit/secrets.toml
nano .streamlit/secrets.toml

rm .streamlit/secrets.toml
'''


import streamlit as st
import gspread
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Auth: Auto-switch between local and cloud
def authorize_gspread():
    try:
        from google.oauth2.service_account import Credentials
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        return gspread.authorize(creds)
    except Exception:
        from oauth2client.service_account import ServiceAccountCredentials
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("gspread_service_account.json", scope)
        return gspread.authorize(creds)

gc = authorize_gspread()

# Load Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ah_-_4cDJx-jKgBbSKBroyesnInBPxi0ow-dssnFVRg/edit#gid=0"
sheet = gc.open_by_url(SHEET_URL)
worksheet = sheet.sheet1

# Data functions
def get_data():
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

def add_entry(entry):
    worksheet.append_row(entry)

def update_entry(date, updated_entry):
    data = worksheet.get_all_values()
    for i, row in enumerate(data[1:], start=2):  # Skip header
        if row[0] == date:
            worksheet.update(f'A{i}:J{i}', [updated_entry])
            return True
    return False

def delete_entry(date):
    data = worksheet.get_all_values()
    for i, row in enumerate(data[1:], start=2):
        if row[0] == date:
            worksheet.delete_rows(i)
            return True
    return False

# UI
st.set_page_config(page_title="Health Tracker", layout="wide")
st.title("🧘 Health & Weight Tracker")
menu = st.sidebar.radio("Menu", ["📈 Dashboard", "➕ Add Entry", "✏️ Update Entry", "❌ Delete Entry"])

df = get_data()

if menu == "📈 Dashboard":
    st.subheader("📊 Progress Overview")
    st.dataframe(df)

    if not df.empty:
        df["DATE"] = pd.to_datetime(df["DATE"])
        df = df.sort_values("DATE")
        fig, ax = plt.subplots()
        ax.plot(df["DATE"], df["TARGET_WEIGHT"], label="Target Weight", linestyle="--")
        ax.plot(df["DATE"], df["CURRENT_WEIGHT"], label="Current Weight", marker="o")
        ax.set_xlabel("Date")
        ax.set_ylabel("Weight (kg)")
        ax.set_title("Progress vs Target")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("No data to display yet.")

elif menu == "➕ Add Entry":
    st.subheader("Add New Entry")
    with st.form("add_entry"):
        date = st.date_input("Date", value=datetime.today())
        target_weight = st.number_input("Target Weight", min_value=30.0, max_value=200.0)
        current_weight = st.number_input("Current Weight", min_value=30.0, max_value=200.0)
        steps = st.number_input("Steps Walked", min_value=0)
        yoga = st.checkbox("Yoga Done?")
        breathing = st.checkbox("Breathing Done?")
        bp = st.text_input("Blood Pressure", value="120/80")
        sugar = st.text_input("Fasting Sugar", value="95")
        mood = st.text_input("Mood/Journal")
        comments = st.text_area("Comments")

        if st.form_submit_button("Submit"):
            add_entry([
                date.strftime("%Y-%m-%d"),
                target_weight,
                current_weight,
                steps,
                "Yes" if yoga else "No",
                "Yes" if breathing else "No",
                bp,
                sugar,
                mood,
                comments
            ])
            st.success("✅ Entry added successfully!")

elif menu == "✏️ Update Entry":
    st.subheader("Update Existing Entry")
    date_to_update = st.text_input("Enter Date to Update (YYYY-MM-DD)")
    if st.button("Load Entry"):
        row = df[df["DATE"] == date_to_update]
        if not row.empty:
            row = row.iloc[0]
            with st.form("update_entry"):
                target_weight = st.number_input("Target Weight", value=float(row["TARGET_WEIGHT"]))
                current_weight = st.number_input("Current Weight", value=float(row["CURRENT_WEIGHT"]))
                steps = st.number_input("Steps Walked", value=int(row["STEPS"]))
                yoga = st.checkbox("Yoga Done?", value=row["YOGA"] == "Yes")
                breathing = st.checkbox("Breathing Done?", value=row["BREATHING"] == "Yes")
                bp = st.text_input("Blood Pressure", value=row["BLOOD_PRESSURE"])
                sugar = st.text_input("Fasting Sugar", value=row["FASTING_SUGAR"])
                mood = st.text_input("Mood/Journal", value=row["MOOD_JOURNAL"])
                comments = st.text_area("Comments", value=row["COMMENTS"])
                if st.form_submit_button("Update"):
                    success = update_entry(date_to_update, [
                        date_to_update,
                        target_weight,
                        current_weight,
                        steps,
                        "Yes" if yoga else "No",
                        "Yes" if breathing else "No",
                        bp,
                        sugar,
                        mood,
                        comments
                    ])
                    if success:
                        st.success("✅ Entry updated.")
                    else:
                        st.error("❌ Entry not found.")
        else:
            st.error("❌ No entry found for that date.")

elif menu == "❌ Delete Entry":
    st.subheader("Delete Entry")
    date_to_delete = st.text_input("Enter Date to Delete (YYYY-MM-DD)")
    if st.button("Delete Entry"):
        if delete_entry(date_to_delete):
            st.success("✅ Entry deleted.")
        else:
            st.error("❌ Entry not found.")
