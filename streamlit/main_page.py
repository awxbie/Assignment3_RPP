import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- Streamlit config ---
st.set_page_config(page_title="Prediksi Kualitas Udara", page_icon="🎈")
st_autorefresh(interval=5000, key="refresh")  # 🔁 Auto-refresh every 5s

st.title("Prediksi Kualitas Udara")
st.sidebar.markdown("# Main page 🎈")

# --- Fetch prediction from FastAPI ---
predicted_ppm = "-"
try:
    prediction_response = requests.get("http://192.168.218.119:8000/predict", timeout=3)
    result = prediction_response.json()
    predicted_ppm = result.get("predicted_ppm", -1)
    prediction_response.close()
except Exception as e:
    st.error(f"❌ Prediction fetch error: {e}")

# --- Fetch MongoDB data ---
mongo_df = pd.DataFrame()
try:
    mongo_response = requests.get("http://192.168.218.119:5000/sensor", timeout=3)
    mongo_data = mongo_response.json().get("data", [])
    mongo_df = pd.DataFrame(mongo_data)
    mongo_response.close()

    if not mongo_df.empty and "timestamp" in mongo_df.columns:
        mongo_df["timestamp"] = pd.to_datetime(mongo_df["timestamp"])
        mongo_df["ppm"] = pd.to_numeric(mongo_df["ppm"], errors="coerce")  # clean ppm values
        mongo_df = mongo_df[["timestamp", "temperature", "humidity", "adc_value", "ppm"]]
        mongo_df = mongo_df.sort_values(by="timestamp", ascending=False).head(10)
        mongo_df.index = range(1, len(mongo_df) + 1)
except Exception as e:
    st.error(f"❌ MongoDB fetch error: {e}")

# --- Layout display ---
left_column, right_column = st.columns(2)

with left_column:
    st.subheader("📊 Sensor Data")
    if not mongo_df.empty:
        st.dataframe(mongo_df)
    else:
        st.info("No sensor data yet.")

with right_column:
    st.subheader("🤖 AI Prediction")
    st.metric(label="Predicted CO (PPM)", value=predicted_ppm)
