
'''
cd /Users/shyamdk/developer/aone/trading/tracker/tracker-clean

If clone is required...

git clone https://github.com/shyamdk/tracker.git


git pull origin main





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

----------------

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
from oauth2client.service_account import ServiceAccountCredentials

# ------------------ AUTH ------------------
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

# ------------------ SHEET INIT ------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ah_-_4cDJx-jKgBbSKBroyesnInBPxi0ow-dssnFVRg/edit#gid=0"
sheet = gc.open_by_url(SHEET_URL)
daily_ws = sheet.sheet1

# 🛠️ Auto-create Task Tracker sheet if not present
def get_or_create_task_sheet(sheet):
    expected_headers = ["ADD_DATE", "TASK", "TARGET_DATE", "TASK_CATEGORY", "TASK_TYPE", "STATUS", "COMMENTS"]
    try:
        task_ws = sheet.worksheet("Task Tracker")
        headers = task_ws.row_values(1)
        if headers != expected_headers:
            task_ws.clear()
            task_ws.append_row(expected_headers)
    except:
        task_ws = sheet.add_worksheet(title="Task Tracker", rows="100", cols="10")
        task_ws.append_row(expected_headers)
    return task_ws

task_ws = get_or_create_task_sheet(sheet)

# ------------------ DAILY TRACKER UTILS ------------------
def get_daily_data():
    return pd.DataFrame(daily_ws.get_all_records())

def add_daily_entry(entry):
    daily_ws.append_row(entry)

def update_daily_entry(date, updated_entry):
    data = daily_ws.get_all_values()
    for i, row in enumerate(data[1:], start=2):
        if row[0] == date:
            daily_ws.update(f'A{i}:J{i}', [updated_entry])
            return True
    return False

def delete_daily_entry(date):
    data = daily_ws.get_all_values()
    for i, row in enumerate(data[1:], start=2):
        if row[0] == date:
            daily_ws.delete_rows(i)
            return True
    return False

# ------------------ TASK TRACKER UTILS ------------------
def get_task_data():
    records = task_ws.get_all_records()
    return pd.DataFrame(records)

def add_task(task_entry):
    task_ws.append_row(task_entry)

def modify_task(add_date, updated_task):
    data = task_ws.get_all_values()
    for i, row in enumerate(data[1:], start=2):
        if row[0] == add_date:
            task_ws.update(f'A{i}:G{i}', [updated_task])
            return True
    return False

def delete_task(add_date):
    data = task_ws.get_all_values()
    for i, row in enumerate(data[1:], start=2):
        if row[0] == add_date:
            task_ws.delete_rows(i)
            return True
    return False

# ------------------ UI ------------------
st.set_page_config(page_title="Health & Task Tracker", layout="wide")
st.title("🧘 Health & Task Tracker")

menu_section = st.sidebar.selectbox("Main Menu", ["📅 Daily Tracker", "📝 Task Tracker"])

# ========== DAILY TRACKER ==========
if menu_section == "📅 Daily Tracker":
    sub_menu = st.sidebar.radio("Daily Tracker", ["📈 Dashboard", "➕ Add Entry", "✏️ Update Entry", "❌ Delete Entry"])
    df = get_daily_data()

    if sub_menu == "📈 Dashboard":
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

    elif sub_menu == "➕ Add Entry":
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
                add_daily_entry([
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

    elif sub_menu == "✏️ Update Entry":
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
                        success = update_daily_entry(date_to_update, [
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
                        st.success("✅ Entry updated." if success else "❌ Entry not found.")

    elif sub_menu == "❌ Delete Entry":
        st.subheader("Delete Entry")
        date_to_delete = st.text_input("Enter Date to Delete (YYYY-MM-DD)")
        if st.button("Delete Entry"):
            st.success("✅ Entry deleted.") if delete_daily_entry(date_to_delete) else st.error("❌ Entry not found.")

# ========== TASK TRACKER ==========
elif menu_section == "📝 Task Tracker":
    sub_menu = st.sidebar.radio("Task Tracker", ["📋 Dashboard", "➕ Add Task", "✏️ Modify Task", "❌ Delete Task"])
    task_df = get_task_data()

    if "STATUS" not in task_df.columns:
        st.warning("⚠️ Task Tracker sheet is missing expected 'STATUS' column. Please check or reinitialize the sheet.")
        st.stop()

    if sub_menu == "📋 Dashboard":
        st.subheader("🧮 Task Dashboard")
        filtered_df = task_df[task_df["STATUS"].isin(["Pending", "In Progress"])]
        if filtered_df.empty:
            st.info("No pending or in-progress tasks.")
        else:
            grouped = filtered_df.groupby("TASK_CATEGORY")
            for cat, group in grouped:
                st.markdown(f"### 📂 {cat}")
                sorted_group = group.sort_values(by="TASK_TYPE", ascending=True)
                st.dataframe(sorted_group)

    elif sub_menu == "➕ Add Task":
        st.subheader("Add New Task")
        with st.form("add_task"):
            add_date = datetime.today().strftime("%Y-%m-%d")
            task = st.text_input("Task")
            target_date = st.date_input("Target Date")
            category = st.text_input("Task Category")
            task_type = st.selectbox("Task Type", ["Important and Urgent", "Important", "Urgent", "Optional"])
            status = st.selectbox("Status", ["Pending", "In Progress", "Done"])
            comments = st.text_area("Comments")
            if st.form_submit_button("Add Task"):
                add_task([add_date, task, target_date.strftime("%Y-%m-%d"), category, task_type, status, comments])
                st.success("✅ Task added.")

    elif sub_menu == "✏️ Modify Task":
        st.subheader("Modify Existing Task")
        add_date = st.text_input("Enter ADD_DATE of Task to Modify (YYYY-MM-DD)")
        task_row = task_df[task_df["ADD_DATE"] == add_date]
        if st.button("Load Task"):
            if not task_row.empty:
                task_row = task_row.iloc[0]
                with st.form("modify_task"):
                    task = st.text_input("Task", value=task_row["TASK"])
                    target_date = st.date_input("Target Date", value=pd.to_datetime(task_row["TARGET_DATE"]))
                    category = st.text_input("Category", value=task_row["TASK_CATEGORY"])
                    task_type = st.selectbox("Task Type", ["Important and Urgent", "Important", "Urgent", "Optional"], index=0)
                    status = st.selectbox("Status", ["Pending", "In Progress", "Done"], index=0)
                    comments = st.text_area("Comments", value=task_row["COMMENTS"])
                    if st.form_submit_button("Update Task"):
                        updated = modify_task(add_date, [add_date, task, target_date.strftime("%Y-%m-%d"), category, task_type, status, comments])
                        st.success("✅ Task updated." if updated else "❌ Task not found.")
            else:
                st.error("❌ No task found.")

    elif sub_menu == "❌ Delete Task":
        st.subheader("Delete Task")
        add_date = st.text_input("Enter ADD_DATE of Task to Delete (YYYY-MM-DD)")
        if st.button("Delete Task"):
            st.success("✅ Task deleted.") if delete_task(add_date) else st.error("❌ Task not found.")
