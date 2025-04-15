from scapy.all import sniff, Raw
from scapy.all import get_if_list
from scapy.layers.inet import IP, TCP, UDP
from collections import defaultdict
import time
import numpy as np
import joblib
import requests

model = joblib.load("intrusion_model.pkl")

# Biến lưu lại các phiên kết nối để thống kê
session_stats = defaultdict(lambda: {
    "timestamps": [],
    "srv_count": 0,
    "same_srv_count": 0,
    "same_src_port_count": 0,
})

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
        1 if proto == 17 else 0,    # protocol_type: UDP = 1, khác = 0
        flag,                       # flag
        src_bytes,                 # src_bytes
        dst_bytes,                 # dst_bytes
        count,                     # count: số gói tin trong 2s gần nhất
        same_srv_rate,            # same_srv_rate
        diff_srv_rate,            # diff_srv_rate
        dst_host_srv_count,       # số kết nối đến cùng host
        dst_host_same_srv_rate,   # tỉ lệ dịch vụ giống nhau
        dst_host_same_src_port_rate  # tỉ lệ trùng port nguồn
    ]


def detect(pkt):
    try:
        print(" Gói tin nhận được:", pkt.summary())  # xem nhanh nội dung gói tin
        features = extract_features(pkt)
        print(" Features truyền vào mô hình:", features)
        x = np.array([features])
        pred = model.predict(x)[0]
        print("🔎 Dự đoán:", pred)

        if pred == 1:
            print(" Phát hiện tấn công!")
            requests.post("http://localhost:5000/api/set_status", json={
                "fire": False,
                "intrusion": "Tấn công mạng",
                "temperature": 30.0,
                "humidity": 50.0
            })

    except Exception as e:
        print(" Lỗi:", e)


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
