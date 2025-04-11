from machine import Pin, ADC, I2C
from time import sleep
import dht
import ssd1306
import urequests as requests
import ujson
import network
import utime as time
import math
import gc


# Device di Ubidots
DEVICE_ID = "esp32"
TOKEN = "BBUS-k8QgRAb8R2POk4Cqa4iElc9c18mgpr"
UBIDOTS_URL = "http://industrial.api.ubidots.com/api/v1.6/devices/{}".format(DEVICE_ID)
HEADERS = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

# MongoDB API
MONGO_API = "http://192.168.218.119:5000/sensor"    # Marcel

# Cara connect Hotspot
def do_connect1():
    import network
    sta_if = network.WLAN(network.WLAN.IF_STA)
    if not sta_if.isconnected():
        print("Connecting to network")
        sta_if.active(True)
        sta_if.connect('Samsung A55', '18072005')
        while not sta_if.isconnected():
            pass
        print('network config:', sta_if.ipconfig('addr4'))

def did_receive_callback(topic, message):
    print('\n\nData Received! \ntopic = {0}, message = {1}'.format(topic, message))

do_connect1();

# --- Inisialisasi DHT11 ---
dht_sensor = dht.DHT11(Pin(33))  # DATA DHT11 di GPIO14
fan = Pin(21, Pin.OUT)

# --- Inisialisasi MQ135 ---
mq135 = ADC(Pin(34))
mq135.atten(ADC.ATTN_11DB)        # Maks input ~3.3V
mq135.width(ADC.WIDTH_12BIT)
divider_ratio = 2.0               # Jika pakai voltage divider 10kΩ + 10kΩ

# --- Inisialisasi OLED (I2C) ---
i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

keepOn = 0
#11220
#21440
#30440

def calculate_ppm(adc):
    Vref = 5
    RL = 30440
    R0 = 7293
    v_out = adc / 4095 * Vref
    rs = ((Vref - v_out) / v_out) * RL
    ratio = rs / R0
    return round(pow(10, (-0.42 * math.log10(ratio) + 1.92)), 2)

while True:
    try:
        # Baca DHT11
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()

        # Baca MQ135
        adc_value = mq135.read()
        v_adc = adc_value / 4095 * 3.3
        v_input = v_adc * divider_ratio
        ppm = calculate_ppm(adc_value)

        # Debug via serial juga (opsional)
        print("Temp:", temp, "C | Hum:", hum, "% | ADC:", adc_value, "% | PPM:", ppm, "PPM")
        
        # Kirim ke Ubidots
        data = {
            "temperature": temp,
            "humidity": hum,
            "ppm": ppm,
            "adc_value": adc_value
        }
        response = requests.post(UBIDOTS_URL, json=data, headers=HEADERS, timeout=5)
        print("Ubidots status:", response.status_code)
        response.close()
        
        # Kirim ke MongoDB
        data_mongo = {
            "temperature": temp,
            "humidity": hum,
            "adc_value": adc_value,
            "ppm": ppm,
#             "led": 0  # nanti bisa kamu isi dengan prediksi AI
        }
        response = requests.post(MONGO_API, json=data_mongo, timeout=5)
        print("MongoDB status:", response.status_code)
        response.close()
        
        try:
            # Replace with your actual PC IP address
            prediction_response = requests.get("http://192.168.218.119:8000/predict")
            result = prediction_response.json()
            predicted_ppm = result.get("predicted_ppm", -1)
            prediction_response.close()
            del prediction_response

            print("Predicted PPM from FastAPI:", predicted_ppm)

            # Optional: Control a fan on GPIO pin 12
            # fan = Pin(21, Pin.OUT)
            if predicted_ppm > 22 :
                fan.on()
                keepOn = 3
                print("⚠️ High PPM! Fan ON")
                
            elif keepOn > 0:
                fan.on()
                keepOn -= 1
                print(f"Fan ON (cooldown: {keepOn} loops left)")    
            
            else:
                fan.off()
                print("✅ PPM Normal. Fan OFF")

            
        except Exception as e:
            print("Error fetching prediction:", e)

         # Tampilkan di OLED
        oled.fill(0)  # clear screen
        oled.text("Temp: {} C".format(temp), 0, 0)
        oled.text("Hum : {} %".format(hum), 0, 10)
        oled.text("ADC : {}".format(adc_value), 0, 20)
        oled.text("PPM : {:.2f} PPM".format(ppm), 0, 30)
        if predicted_ppm is not None:
            oled.text("Pred: {}ppm".format(int(predicted_ppm)), 0, 40)
        
        oled.show()

    except Exception as e:
        print("Error:", e)
    
    gc.collect()
    sleep(2)
    

