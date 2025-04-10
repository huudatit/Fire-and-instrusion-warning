from scapy.all import sniff, Raw
import numpy as np
import joblib
import requests

model = joblib.load("intrusion_model.pkl")

def extract_features(pkt):
    return [
        1 if pkt.haslayer("UDP") else 0,
        1,
        len(pkt[Raw]) if pkt.haslayer("Raw") else 0,
        0,
        100,
        0.1,
        0.3,
        200,
        0.2,
        0.4
    ]

def detect(pkt):
    try:
        features = extract_features(pkt)
        x = np.array([features])
        pred = model.predict(x)[0]
        if pred == 1:
            print(" Phát hiện tấn công!")
            requests.post("http://localhost:5000/api/set_status", json={
                "fire": False,
                "intrusion": "Tấn công mạng",
                "temperature": 30.0,
                "humidity": 50.0
            })
    except Exception as e:
        print("Lỗi:", e)

sniff(filter="tcp port 5000", prn=detect, store=0)
