from scapy.all import sniff, Raw
from scapy.all import get_if_list
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


# def detect(pkt):
#     print(pkt.summary())  # In mọi gói tin

sniff(
    filter="tcp port 5000",
    iface="\\Device\\NPF_{C4639796-7D93-4826-B4DF-7DAB5BFAA2D4}",
    prn=detect,
    store=0
)
print(get_if_list())



#test interface
# from scapy.all import sniff, get_if_list

# print("Available interfaces:")
# interfaces = get_if_list()
# for i, iface in enumerate(interfaces):
#     print(f"[{i}] {iface}")

# # Chạy thử 1 interface một cách thủ công để kiểm tra hoạt động
# def test_interface(index):
#     iface = interfaces[index]
#     print(f"\n⏳ Testing interface: {iface}...")
#     sniff(iface=iface, prn=lambda pkt: print(f"[{iface}] {pkt.summary()}"), count=5, timeout=10)

# # Ví dụ: thử interface số 0
# test_interface(4)
