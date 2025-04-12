import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from model.predict_model import fetch_last_10_ppm, predict_next_ppm

# --- Streamlit config ---
st.set_page_config(page_title="Prediksi Kualitas Udara", page_icon="🎈")
st_autorefresh(interval=5000, key="refresh")  # 🔁 Auto-refresh every 5s

st.title("Prediksi Kualitas Udara")
st.sidebar.markdown("# Main page 🎈")

# --- Fetch MongoDB data ---
mongo_docs = fetch_last_10_ppm()
mongo_df = pd.DataFrame(mongo_docs)

if not mongo_df.empty and "timestamp" in mongo_df.columns:
    mongo_df["timestamp"] = pd.to_datetime(mongo_df["timestamp"])
    mongo_df["ppm"] = pd.to_numeric(mongo_df["ppm"], errors="coerce")
    
    # Check available columns
    available_columns = ["timestamp", "temperature", "humidity", "adc_value", "ppm"]
    existing_columns = [col for col in available_columns if col in mongo_df.columns]
    
    # Select only existing columns
    mongo_df = mongo_df[existing_columns]
    
    mongo_df = mongo_df.sort_values(by="timestamp", ascending=False).head(10)
    mongo_df.index = range(1, len(mongo_df) + 1)


# --- Lakukan prediksi lokal ---
predicted_ppm = predict_next_ppm()

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
