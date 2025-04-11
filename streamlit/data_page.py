import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# --- Page setup ---
st.set_page_config(page_title="Data Page", page_icon="🎈")
st_autorefresh(interval=5000, key="history_refresh")  # Auto-refresh every 5 seconds
st.sidebar.markdown("# Data Page 🎈")
st.title("📚 History & 📈 Chart Page")

# --- Fetch sensor data from MongoDB ---
mongo_df = pd.DataFrame()
try:
    response = requests.get("https://fa56-120-188-35-18.ngrok-free.app/sensor", timeout=5)
    data = response.json().get("data", [])
    mongo_df = pd.DataFrame(data)
    response.close()

    # ✅ Convert and sort timestamp
    # Convert timestamp and fix ppm column
    if not mongo_df.empty and "timestamp" in mongo_df.columns:
        mongo_df["timestamp"] = pd.to_datetime(mongo_df["timestamp"])
        mongo_df = mongo_df.sort_values(by="timestamp", ascending=True)

        # ✅ Clean up ppm
        mongo_df = mongo_df[["timestamp", "temperature", "humidity", "adc_value", "ppm"]]

        # ✅ Set index to start at 1
        mongo_df.index = range(1, len(mongo_df) + 1)

except Exception as e:
    st.error(f"❌ Error fetching data: {e}")

# --- Display the full table ---
if not mongo_df.empty:
    st.subheader("📊 Full Sensor Data Table")
    st.dataframe(
        mongo_df[["timestamp", "temperature", "humidity", "adc_value", "ppm"]],
        use_container_width=True
    )
else:
    st.warning("No data available to display.")

# --- Initialize session state for chart control ---
if "show_chart" not in st.session_state:
    st.session_state.show_chart = False
if "chart_column" not in st.session_state:
    st.session_state.chart_column = None

# --- Chart selection form ---
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

# --- Display line chart if selected ---
if st.session_state.show_chart and st.session_state.chart_column:
    st.subheader(f"📈 {st.session_state.chart_column.title()} Over Time")

    chart_df = mongo_df[["timestamp", st.session_state.chart_column]]
    chart_df = chart_df.rename(columns={st.session_state.chart_column: "value"})

    st.line_chart(data=chart_df, x="timestamp", y="value", use_container_width=True)
