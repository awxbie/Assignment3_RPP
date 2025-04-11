from fastapi import FastAPI
from pymongo import MongoClient
import numpy as np
from tensorflow.keras.models import load_model
import joblib

app = FastAPI()

# --- Load model and scaler ---
model = load_model("lstm_model.keras")
scaler = joblib.load("scaler.pkl")

# --- Connect to MongoDB Atlas ---
mongo_uri = "mongodb+srv://rpp:rpp12345@rpp.jtumn.mongodb.net/?retryWrites=true&w=majority&appName=RPP"
client = MongoClient(mongo_uri)
db = client["SensorDatabase1"]
collection = db["DataSensor1"]

@app.get("/predict")
def predict_ppm():
    try:
        # --- Fetch last 10 ppm readings from MongoDB ---
        cursor = collection.find({}, {"_id": 0, "ppm": 1}).sort("timestamp", -1).limit(10)
        docs = list(cursor)
        docs.reverse()  # make them oldest → newest

        if len(docs) < 10:
            return {"error": "Not enough data to predict (need 10 ppm readings)."}

        ppm_values = [doc["ppm"] for doc in docs]

        # --- Preprocess for LSTM ---
        X = scaler.transform(np.array(ppm_values).reshape(-1, 1)).reshape(1, 10, 1)

        # --- Predict next ppm ---
        predicted_scaled = model.predict(X)
        predicted_ppm = float(scaler.inverse_transform(predicted_scaled)[0][0])

        return {"predicted_ppm": round(predicted_ppm, 2)}

    except Exception as e:
        return {"error": str(e)}

