import numpy as np
import os
import streamlit as st
import joblib
from tensorflow.keras.models import load_model
from pymongo import MongoClient

# --- Load model and scaler only once ---
@st.cache_resource
def load_model_and_scaler():
    base_path = os.path.dirname(__file__)
    model = load_model(os.path.join(base_path, "lstm_model.keras"))
    scaler = joblib.load(os.path.join(base_path, "scaler.pkl"))
    return model, scaler

model, scaler = load_model_and_scaler()

# --- Load MongoDB data ---
@st.cache_data(ttl=60)
def fetch_last_10_ppm():
    try:
        uri = st.secrets["mongo"]["uri"]
        client = MongoClient(uri)
        db = client["SensorDatabase1"]
        collection = db["DataSensor1"]

        cursor = collection.find({}, {"_id": 0, "ppm": 1, "timestamp": 1}).sort("timestamp", -1).limit(10)
        docs = list(cursor)
        docs.reverse()
        return docs
    except Exception as e:
        st.error(f"Gagal mengambil data MongoDB: {e}")
        return []

# --- Predict function ---
def predict_next_ppm():
    docs = fetch_last_10_ppm()

    if len(docs) < 10:
        return "❌ Not enough data"

    ppm_values = [doc["ppm"] for doc in docs]
    X = scaler.transform(np.array(ppm_values).reshape(-1, 1)).reshape(1, 10, 1)

    y_scaled = model.predict(X)
    y_pred = scaler.inverse_transform(y_scaled)[0][0]
    return round(float(y_pred), 2)
