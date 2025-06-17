from scapy.all import sniff, Raw
from scapy.all import get_if_list
from scapy.layers.inet import IP, TCP, UDP
from collections import defaultdict
import time
import threading
import numpy as np
import pandas as pd
import joblib
import requests
import json
from collections import defaultdict, deque
import time

model = joblib.load("intrusion_model.pkl")
scaler = joblib.load("scaler.pkl")  # Load bộ chuẩn hóa

timestamps = deque()
total_sniff_calls = 0
error_count = 0

feature_names = [
    'protocol_type','service','flag','src_bytes','dst_bytes',
    'count','same_srv_rate','diff_srv_rate',
    'dst_host_srv_count','dst_host_same_srv_rate'
]

# Biến lưu lại các phiên kết nối để thống kê
session_stats = defaultdict(lambda: {
    "timestamps": [],
    "srv_count": 0,
    "same_srv_count": 0,
    "same_src_port_count": 0,
})

# # Thêm biến toàn cục theo dõi thời gian cuối cùng phát hiện tấn công
# last_attack_time = 0
# last_status = "Bình thường"
# Threshold gói trong 2s để được xem là tấn công
ATTACK_THRESHOLD = 3

def extract_features(pkt):
    if not pkt.haslayer(IP):
        return None  # Không có IP => bỏ

    ip = pkt[IP]
    proto = ip.proto  # 6: TCP, 17: UDP
    src_ip = ip.src
    dst_ip = ip.dst
    src_port = pkt[TCP].sport if pkt.haslayer(TCP) else (pkt[UDP].sport if pkt.haslayer(UDP) else 0)
    dst_port = pkt[TCP].dport if pkt.haslayer(TCP) else (pkt[UDP].dport if pkt.haslayer(UDP) else 0)

    session_key = f"{src_ip}:{src_port} → {dst_ip}:{dst_port}"

    # Thêm timestamp để tính count trong 2 giây gần nhất
    now = time.time()
    #session_stats[session_key]["timestamps"].append(now)
    # Nếu đã quá 2s không có gói nào thì reset lại toàn bộ stats cho session này
    if session_stats[session_key]["timestamps"]:
        last_time = session_stats[session_key]["timestamps"][-1]
        if now - last_time > 2:
            session_stats.pop(session_key)
            session_stats[session_key] = {
                "timestamps": [],
                "srv_count": 0,
                "same_srv_count": 0,
                "same_src_port_count": 0,
            }

    session_stats[session_key]["timestamps"].append(now)

    # Lọc chỉ các gói trong 2s gần nhất
    session_stats[session_key]["timestamps"] = [
        t for t in session_stats[session_key]["timestamps"] if now - t < 2
    ]
    count = len(session_stats[session_key]["timestamps"])

    # Xác định dịch vụ dựa vào port (đơn giản hóa)
    common_services = {80: 'http', 443: 'https', 21: 'ftp', 22: 'ssh'}
    service = common_services.get(dst_port, 'other')
    same_srv_rate = 1.0 if service != 'other' else 0.0
    diff_srv_rate = 1.0 - same_srv_rate

    # Tính các chỉ số liên quan đến destination
    session_stats[session_key]["srv_count"] += 1
    if dst_port == 80:
        session_stats[session_key]["same_srv_count"] += 1
    if src_port == dst_port:
        session_stats[session_key]["same_src_port_count"] += 1

    dst_host_srv_count = session_stats[session_key]["srv_count"]
    dst_host_same_srv_rate = session_stats[session_key]["same_srv_count"] / dst_host_srv_count
    dst_host_same_src_port_rate = session_stats[session_key]["same_src_port_count"] / dst_host_srv_count

    # Trích xuất src_bytes và dst_bytes
    src_bytes = len(pkt[Raw]) if pkt.haslayer(Raw) else 0
    dst_bytes = pkt.len - src_bytes if hasattr(pkt, 'len') else 0

    # Gán flag = 1 nếu là TCP SYN
    flag = 1 if pkt.haslayer(TCP) and pkt[TCP].flags == 'S' else 0

    return [
        1 if proto == 17 else 0,      # protocol_type
        1.0 if service != 'other' else 0.0,  # service (binary)
        flag,                         # flag
        src_bytes,                    # src_bytes
        dst_bytes,                    # dst_bytes
        count,                        # count
        same_srv_rate,               # same_srv_rate
        diff_srv_rate,               # diff_srv_rate
        dst_host_srv_count,          # dst_host_srv_count
        dst_host_same_srv_rate       # dst_host_same_srv_rate
    ]



def detect(pkt):
    global total_sniff_calls, timestamps, error_count
    
    # 1) Tính throughput: số packet trong 1s gần nhất
    now = time.time()
    timestamps.append(now)
    while timestamps and now - timestamps[0] > 1.0:
        timestamps.popleft()
    throughput = len(timestamps)  # pkt/s
    # 2) Bắt đầu đo latency
    total_sniff_calls += 1
    start = time.time()

    features = extract_features(pkt)
    if features is None:
        return
    x = pd.DataFrame([features], columns=feature_names)
    x_scaled = scaler.transform(x)
    pred = model.predict(x_scaled)[0]

    # 3) Tính latency
    latency_ms = (time.time() - start) * 1000

    time.sleep(1)
     # 4) In metric
    print(f"[METRIC][monitor] Packet #{total_sniff_calls}: "
          f"latency={latency_ms:.2f} ms, throughput={throughput} pkt/s")
    try:
        with open("status.json", "r") as f:
            current_status = json.load(f)
    except:
        current_status = {"temperature": 30.0, "humidity":50.0}

    payload = {
        "fire": False,
        "intrusion": "Tấn công mạng" if pred == 1 and features[4] > ATTACK_THRESHOLD else "Bình thường",
        "temperature": current_status.get("temperature", 30.0),
        "humidity":    current_status.get("humidity", 50.0),
        "source":      "monitor"
    }
    
    print(" Gói tin:", pkt.summary())
    print(" Features truyền vào mô hình:", features)
    print(" Dự đoán:", pred)
    if pred == 1 and features[4] > ATTACK_THRESHOLD:
        print(" Phát hiện tấn công!")

    
    # try:
    #     with open("status.json", "r") as f:
    #         current_status = json.load(f)
    # except:
    #     current_status = {"temperature": 30.0, "humidity": 50.0}  # fallback

    #     payload = {
    #         "fire": False,
    #         "intrusion": "Tấn công mạng" if pred == 1 and features[4] > ATTACK_THRESHOLD else "Bình thường",
    #         "temperature": current_status.get("temperature", 30.0),
    #         "humidity": current_status.get("humidity", 50.0),
    #         "source": "monitor"
    #     }

    #     # if pred == 1 and features[4] > ATTACK_THRESHOLD:
    #     #     print("Phát hiện tấn công!")
    try:    
        requests.post("http://localhost:5000/api/set_status", json=payload)

    except Exception as e:
        error_count += 1
        print(f"[ERROR][monitor] POST /api/set_status failed: {e}")

    # --- tính và in Error Rate ---
    error_rate = error_count / total_sniff_calls * 100
    print(f"[METRIC][monitor] Error Rate: {error_rate:.2f}% ({error_count}/{total_sniff_calls})\n")



sniff(
    #filter="tcp port 5000",
    iface="\\Device\\NPF_{C4639796-7D93-4826-B4DF-7DAB5BFAA2D4}",
    prn=detect,
    store=0
)
print(get_if_list())


# #test interface
# from scapy.all import sniff, get_if_list

# print("Available interfaces:")
# interfaces = get_if_list()
# for i, iface in enumerate(interfaces):
#     print(f"[{i}] {iface}")

# # Chạy thử 1 interface một cách thủ công để kiểm tra hoạt động
# def test_interface(index):
#     iface = interfaces[index]
#     print(f"\n Testing interface: {iface}...")
#     sniff(iface=iface, prn=lambda pkt: print(f"[{iface}] {pkt.summary()}"), count=5, timeout=10)

# # Ví dụ: thử interface số 0
# test_interface(4)

