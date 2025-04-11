from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

app = Flask(__name__)

# --- Koneksi MongoDB ---
uri = "mongodb+srv://rpp:rpp12345@rpp.jtumn.mongodb.net/?retryWrites=true&w=majority&appName=RPP"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ MongoDB Error:", e)

# --- Pilih Database dan Collection ---
db = client['SensorDatabase1']
sensor_collection = db['DataSensor1']

# --- Simpan data ke MongoDB ---
def store_data(data):
    result = sensor_collection.insert_one(data)
    return result.inserted_id

# --- Ambil semua data dari MongoDB ---
def get_data():
    return list(sensor_collection.find({}, {"_id": 0}))  # tanpa _id agar JSON lebih bersih

# --- Endpoint: Simpan Data dari ESP32 ---
@app.route('/sensor', methods=['POST'])
def store_sensor_data():
    try:
        body = request.get_json()

        temperature = body.get('temperature', 0)
        humidity = body.get('humidity', 0)
        adc_value = body.get('adc_value', 0)
        ppm = body.get('ppm', 0)

        data_to_store = {
            "temperature": temperature,
            "humidity": humidity,
            "adc_value": adc_value,
            "ppm": ppm,
            "timestamp": datetime.utcnow()
        }

        store_data(data_to_store)

        return jsonify({"message": "✅ Data stored successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Endpoint: Ambil semua data ---
@app.route('/sensor', methods=['GET'])
def get_sensor_data():
    try:
        data = get_data()
        return jsonify({"message": "✅ Data retrieved successfully!", "data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run Server ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
