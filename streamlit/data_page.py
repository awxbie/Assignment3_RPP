import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from model.predict_model import fetch_last_10_ppm, predict_next_ppm
from pymongo import MongoClient

# --- Page setup ---
st.set_page_config(page_title="Data Page", page_icon="🎈")
st_autorefresh(interval=5000, key="history_refresh")  # Auto-refresh every 5 seconds
st.sidebar.markdown("# Data Page 🎈")
st.title("📚 History & 📈 Chart Page")

# --- Fetch full data from MongoDB (not just 10) ---
def fetch_full_data():
    try:
        uri = st.secrets["mongo"]["uri"]
        client = MongoClient(uri)
        db = client["SensorDatabase1"]
        collection = db["DataSensor1"]
        cursor = collection.find({}, {"_id": 0, "timestamp": 1, "temperature": 1, "humidity": 1, "adc_value": 1, "ppm": 1}).sort("timestamp", 1)
        return list(cursor)
    except Exception as e:
        st.error(f"❌ Error fetching MongoDB data: {e}")
        return []

# --- Convert to DataFrame ---
mongo_docs = fetch_full_data()
mongo_df = pd.DataFrame(mongo_docs)

if not mongo_df.empty and "timestamp" in mongo_df.columns:
    mongo_df["timestamp"] = pd.to_datetime(mongo_df["timestamp"])
    mongo_df = mongo_df[["timestamp", "temperature", "humidity", "adc_value", "ppm"]]
    mongo_df.index = range(1, len(mongo_df) + 1)

# --- Display full table ---
if not mongo_df.empty:
    st.subheader("📊 Full Sensor Data Table")
    st.dataframe(mongo_df, use_container_width=True)
else:
    st.warning("No data available to display.")

# --- Chart control session ---
if "show_chart" not in st.session_state:
    st.session_state.show_chart = False
if "chart_column" not in st.session_state:
    st.session_state.chart_column = None

# --- Chart selection ---
with st.form("line_chart_form"):
    st.markdown("### 📈 Line Chart Selector")

    option = st.selectbox(
        "What data would you like to visualize?",
        ("temperature", "humidity", "adc_value", "ppm")
    )

    col1, col2 = st.columns([1, 1])
    submit = col1.form_submit_button("Submit")
    reset = col2.form_submit_button("Reset")

    if submit:
        st.session_state.chart_column = option
        st.session_state.show_chart = True
    if reset:
        st.session_state.chart_column = None
        st.session_state.show_chart = False

# --- Display chart ---
if st.session_state.show_chart and st.session_state.chart_column:
    st.subheader(f"📈 {st.session_state.chart_column.title()} Over Time")

    chart_df = mongo_df[["timestamp", st.session_state.chart_column]].rename(
        columns={st.session_state.chart_column: "value"}
    )
    st.line_chart(data=chart_df, x="timestamp", y="value", use_container_width=True)
