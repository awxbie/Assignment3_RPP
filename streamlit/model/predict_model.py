import numpy as np
import os
import streamlit as st
import joblib
from tensorflow.keras.models import load_model
from pymongo import MongoClient

# --- Load LSTM model and scaler only once ---
@st.cache_resource
def load_lstm_and_scaler():
    base_path = os.path.dirname(__file__)
    model = load_model(os.path.join(base_path, "lstm_model.keras"))
    scaler = joblib.load(os.path.join(base_path, "scaler.pkl"))
    return model, scaler

lstm_model, scaler = load_lstm_and_scaler()

# --- Load classification model only once ---
@st.cache_resource
def load_classification_model():
    try:
        base_path = os.path.dirname(__file__)
        model = joblib.load(os.path.join(base_path, "air_quality_model.sav"))
        return model
    except Exception as e:
        st.error(f"❌ Gagal memuat model klasifikasi: {e}")
        return None

classification_model = load_classification_model()

# --- Fetch last 10 ppm from MongoDB ---
@st.cache_data(ttl=60)
def fetch_last_10_ppm():
    try:
        uri = st.secrets["mongo"]["uri"]
        client = MongoClient(uri)
        db = client["SensorDatabase1"]
        collection = db["DataSensor1"]

        cursor = collection.find({}, {"_id": 0, "ppm": 1, "temperature": 1, "humidity": 1, "timestamp": 1}).sort("timestamp", -1).limit(10)
        docs = list(cursor)
        docs.reverse()
        return docs
    except Exception as e:
        st.error(f"Gagal mengambil data MongoDB: {e}")
        return []

# --- Predict next PPM and classify air quality ---
def predict_next_ppm_with_classification():
    docs = fetch_last_10_ppm()

    if len(docs) < 10:
        return "❌ Not enough data", "N/A"

    # Extract ppm for sequence model
    ppm_values = [doc["ppm"] for doc in docs]
    X_seq = scaler.transform(np.array(ppm_values).reshape(-1, 1)).reshape(1, 10, 1)

    # Predict next PPM
    y_scaled = lstm_model.predict(X_seq)
    predicted_ppm = scaler.inverse_transform(y_scaled)[0][0]

    # Classify predicted air quality
    if classification_model:
        # Use latest avg temperature & humidity from Mongo
        temperatures = [doc.get("temperature", 0) for doc in docs if "temperature" in doc]
        humidities = [doc.get("humidity", 0) for doc in docs if "humidity" in doc]

        avg_temp = np.mean(temperatures)
        avg_hum = np.mean(humidities)

        input_features = np.array([[predicted_ppm, avg_temp, avg_hum]])
        label = classification_model.predict(input_features)[0]
    else:
        label = "Unknown"

    return round(float(predicted_ppm), 2), label
