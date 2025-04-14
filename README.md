# Stage 3 - Assignment 1
## UNI174 - RPP
## Portable Automatic Air Purifier (PAAP)

Dalam proyek ini kami membuat prototype IoT "Portable Automatic Air Purifier" yang dapat mendeteksi kualitas udara dan mengaktifkan sistem penyaringan udara jika kualitas udara disekitarnya tidak baik.

Rangkaian IoT tersebut menggunakan sensor DHT11 dan MQ135 untuk mengambil data suhu, kelembapan, dan kadar gas dalam satuan ADC (output analog dari MQ135). ADC Value tersebut kemudian dikonversi menjadi PPM untuk menunjukkan tingkat polusi di udara.

Data tersebut disimpan di dalam database MongoDB untuk menyimpan data historis, pengiriman data tersebut menggunakan REST API. Selain itu, data tersebut juga dikirim ke Ubidots secara parallel untuk menampilkan visualisasi data suhu, kelembapan dan PPM.

Data tersebut kemudian diambil menggunakan FastAPI dan digunakan oleh model AI LSTM untuk memprediksi hasil data (PPM) yang lebih akurat. Hasil prediksi tersebut menentukan jika Air Purifier pada rangkaian IoT menyala atau tidak.

Selain itu, kami juga membuat dashboard menggunakan Streamlit untuk menampilkan data-data yang penting kepada user.

## File-file:
1. ASS3.py
- Kode tersebut digunakan untuk menjalankan sistem, mengambil data dari sensor, dan mengatur perangkat di rangkaian IoT. Sensor DHT11 digunakan untuk mengambil data suhu dan kelembapan, sedangkan sensor MQ135 digunakan untuk mengambil data kadar gas (ADC Value). Data kadar gas tersebut dikonversikan ke PPM untuk menunjukkan tingkat polusi. Data-data tersebut dikirim ke Ubidots untuk visualisasi data, serta dikirim ke database MongoDB. Kode tersebut kemudian mengambil prediksi PPM dari FastAPI untuk menentukan nyala atau mati kipas (menyala jika prediksi PPM melewati batas tertentu). Data-data tersebut juga ditampilkan pada rangkaian IoT dengan menggunakan layer OLED.

2. DATABASE.py
- Kode tersebut menggunakan Flask untuk menyimpan dan mengambil data sensor dari ESP32 ke database MongoDB. Data dari sensor dikirim melalui metode 'POST' dan disimpan ke database dengan tambahan informasi timestamp. Data dari sensor juga dapat diambil dari database dengan metode 'GET'.

3. lstm_model.keras
- File tersebut merupakan hasil akhir model AI yang telah ditraining. Kami memilih model LSTM (Long Short-Term Memory) karena model LSTM cocok untuk melakukan prediksi dengan data yang fluktuatif. Model ini digunakan untuk memprediksi nilai PPM yang lebih akurat berdasarkan dataset kualitas udara dari Kaggle.

4. main.py
- Kode tersebut digunakan untuk memprediksi nilai PPM udara menggunakan model AI, FastAPI digunakan untuk mengambil data predict secara real-time. Kode tersebut mengambil 10 data PPM terbaru dari MongoDB, menggunakan scaler.pkl untuk normalisasi data, dan kemudian memprosesnya ke dalam model AI LSTM. Hasil prediksi tersebut dikembalikan melalui /predict.

5. Streamlit
- Folder tersebut berisi script-script python yang digunakan untuk visualisasi data. Script tersebut merupakan dashboard berbasis web yang menggunakan Streamlit. Program tersebut terhubung langsung ke FastAPI untuk mengambil informasi data dan prediksi. Visualisasi tersebut dibuat agar user dapat melihat data dan hasil prediksi secara lebih mudah.
- Script python Streamlit tersebut memiliki 2 halaman:
	1.) Main Page
		- Halaman yang menampilkan 10 data terakhir yang digunakan untuk prediksi dan hasil nilai prediksi PPM dari FastAPI.
	2.) Data Page
		- Halaman yang menampilkan table data lengkap dari MongoDB dan visualisasi interaktif grafik yang dapat dipilih oleh user (antara suhu, kelembapan, nilai ADC, atau PPM)
