import requests

url = "http://localhost:5000/api/infer"  # hoặc IP LAN nếu chạy từ máy khác

sample = {
    "protocol_type": 1,
    "flag": 2,
    "src_bytes": 300,
    "dst_bytes": 1000,
    "count": 20,
    "same_srv_rate": 0.7,
    "diff_srv_rate": 0.1,
    "dst_host_srv_count": 50,
    "dst_host_same_srv_rate": 0.8,
    "dst_host_same_src_port_rate": 0.4
}

res = requests.post(url, json=sample)
print("Phản hồi từ server:", res.json())
