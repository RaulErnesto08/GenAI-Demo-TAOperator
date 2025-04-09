# ============================================================
# 📦 IMPORTS & SETUP
# ============================================================
import time
import threading

from utils import *
from actions import *
from config import JDS_PATH, shared_status, set_selected_jd
from agent_runner import run_agent_background
from file_manager import get_output_path_from_jd, load_candidate_data

import streamlit as st

# ============================================================
# 🧠 APP INIT
# ============================================================
st.set_page_config(page_title="LinkedIn Candidate Finder", layout="wide")
st.title("🔍 LinkedIn Candidate Finder")
st.markdown("Automate LinkedIn candidate discovery from a JD and export results to Excel.")

# ============================================================
# 📤 JD UPLOAD SECTION
# ============================================================
st.markdown("### 📤 Upload a Job Description (PDF)")
uploaded_file = st.file_uploader("Upload a new JD", type="pdf")

if uploaded_file:
    # Normalize filename
    clean_name = uploaded_file.name.replace(" ", "_")
    st.session_state.uploaded_filename = clean_name
    dest = JDS_PATH / clean_name

    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File `{clean_name}` uploaded")

    if st.button("✅ Use this JD"):
        st.session_state.selected_jd = clean_name
        st.rerun()

# ============================================================
# 📄 JD SELECTION
# ============================================================
jd_files = list(JDS_PATH.glob("*.pdf"))
jd_names = [file.name for file in jd_files]

# Filename → Pretty title map
jd_display_map = {
    fname: fname.replace(".pdf", "").replace("_", " ") for fname in jd_names
}

if jd_names and "selected_jd" not in st.session_state:
    st.session_state.selected_jd = jd_names[0]

if jd_names:
    selected_jd = st.selectbox(
        "📄 Select a Job Description",
        options=jd_names,
        format_func=lambda x: jd_display_map.get(x, x),
        index=jd_names.index(st.session_state.selected_jd),
    )

    jd_path = str(JDS_PATH / selected_jd)
    job_title = jd_display_map[selected_jd]

    st.session_state.selected_jd = selected_jd
    st.session_state.job_title = job_title
else:
    st.warning("No JDs available. Please upload one to get started.")
    selected_jd = None
    jd_path = None
    job_title = None

# ============================================================
# 🌍 LOCATION FILTER SECTION
# ============================================================
st.markdown("### 🌍 Candidate Location Filters")

default_countries = ["Argentina", "Bolivia", "Chile", "Colombia", "Costa Rica", "Peru", "Mexico"]
selected_countries = ['Costa Rica']

if "candidate_locations" not in st.session_state:
    st.session_state.candidate_locations = default_countries.copy()

selected = st.multiselect(
    "Selected Candidate Locations",
    options=st.session_state.candidate_locations,
    default=st.session_state.get("selected_countries", selected_countries),
    key="location_multiselect",
    help="Choose where you want to search for candidates"
)

new_location = st.text_input(
    "➕ Add a new location", 
    help="Add a country or city manually to the filter", 
    placeholder="e.g. Brazil"
)

if new_location:
    if new_location not in st.session_state.candidate_locations:
        st.session_state.candidate_locations.append(new_location)
        st.session_state.selected_countries.append(new_location)
        st.rerun()

# Always sync final selection
st.session_state.selected_countries = selected

# ============================================================
# 🚀 RUN AGENT SECTION
# ============================================================
def monitor_agent_status_loop():
    status_box = st.empty()
    debug_box = st.empty()

    for _ in range(200):
        current_status = shared_status.get()

        if "__DONE__" in current_status:
            status_box.success("✅ Agent finished successfully!")
            debug_box.code("🎯 Final status: Agent done!")
            break

        elif current_status.startswith("__ERROR__"):
            error_msg = current_status.replace("__ERROR__:", "").strip()
            status_box.error(f"❌ Agent failed: {error_msg}")
            debug_box.code(f"❌ Error: {error_msg}")
            break

        else:
            status_box.markdown(f"### 🔄 {current_status}")
            debug_box.code(f"🔧 Debug: {current_status}")

        time.sleep(3)

    st.rerun()

if st.button("🚀 Run Agent"):
    shared_status.set("Initializing agent...")

    countries = st.session_state.selected_countries
    job_title = st.session_state.job_title

    set_selected_jd(selected_jd)

    threading.Thread(
        target=run_agent_background,
        args=(jd_path, countries, selected_jd),
        daemon=True
    ).start()

    monitor_agent_status_loop()

# ============================================================
# 🧠 FINAL STATUS DISPLAY
# ============================================================
current_status = shared_status.get()
if "✅" in current_status or "❌" in current_status:
    st.success(current_status)
else:
    st.info(f"🧠 Current Status: {current_status}")

# ============================================================
# 📊 RESULTS PREVIEW SECTION
# ============================================================
st.markdown("## 📋 Candidate Results Preview")

view_mode = st.radio("View mode", ["📊 Table View", "📇 Card View"], horizontal=True)

if selected_jd:
    excel_path = get_output_path_from_jd(selected_jd)

    if excel_path.exists():
        candidates = load_candidate_data(excel_path)

        if not candidates:
            st.warning("Excel found, but no candidate rows detected.")
        else:
            if view_mode == "📊 Table View":
                st.dataframe(candidates, use_container_width=True)

            elif view_mode == "📇 Card View":
                for idx, candidate in enumerate(candidates, start=1):
                    with st.expander(f"👤 {candidate['Name']} — {candidate['Match Score']}% Match"):
                        st.markdown(f"**📍 Location:** {candidate['Location']}")
                        st.markdown(f"🔗 [View LinkedIn Profile]({candidate['Profile URL']})", unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("✅ **Matched Skills**")
                            st.markdown(f"<div style='color: green'>{candidate['Matched Skills']}</div>", unsafe_allow_html=True)
                        with col2:
                            st.markdown("❌ **Non-Matched Skills**")
                            st.markdown(f"<div style='color: red'>{candidate['Non-Matched Skills']}</div>", unsafe_allow_html=True)

            with open(excel_path, "rb") as f:
                st.download_button("⬇️ Download Excel", f, file_name=excel_path.name)
    else:
        st.info(f"No candidate results found yet for '{extract_job_title(selected_jd)}'. Run the agent to start the search 🚀")
