import requests
import time
import random

# Địa chỉ Flask server
url = "http://127.0.0.1:5000/api/set_status"

def simulate_data():
    while True:
        payload = {
            "temperature": round(random.uniform(25.0, 60.0), 1),
            "humidity": round(random.uniform(40.0, 90.0), 1),
            "fire": random.choice([True, False]),
            "intrusion": random.choice(["Bình thường", "Tấn công mạng"])
        }

        try:
            res = requests.post(url, json=payload)
            print(f"Gửi dữ liệu: {payload} → Mã phản hồi: {res.status_code}")
        except Exception as e:
            print("Lỗi gửi dữ liệu:", e)

        time.sleep(5)  # Gửi mỗi 5 giây

if __name__ == "__main__":
    simulate_data()
