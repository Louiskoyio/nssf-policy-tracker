import streamlit as st
from PIL import Image
from styles import inject_custom_styles
from app_pages import  (
    view_policies, add_policy, track_contributions,
    add_contributions, bulk_upload, all_policies,upload_schedule,track_schedules
)

# Set page config and styles
st.set_page_config(page_title="NSSF Schedule Tracker", page_icon="assets/small_logo.png", layout="wide")
st.markdown(inject_custom_styles(), unsafe_allow_html=True)

# Logo + Title
logo = Image.open("assets/nssf_logo.jpg")
st.image(logo, width=250)
st.title("NSSF Schedule Tracker")

# Sidebar Menu
menu = [
    "Track Schedules", "Upload Schedule", "Track Contributions",
    "Add Contributions", "Bulk Upload", "All Policies"
]
choice = st.sidebar.selectbox("Menu", menu)

# Route to respective page
if choice == "View Policies":
    view_policies.render()
elif choice == "Upload Schedule":
    upload_schedule.render()
elif choice == "Track Schedules":
    track_schedules.render()
elif choice == "Add Policy":
    add_policy.render()
elif choice == "Track Contributions":
    track_contributions.render()
elif choice == "Add Contributions":
    add_contributions.render()
elif choice == "Bulk Upload":
    bulk_upload.render()
elif choice == "All Policies":
    all_policies.render()


