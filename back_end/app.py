from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
CORS(app)

model = joblib.load("intrusion_model.pkl")
selected_features = [
    'protocol_type', 'flag', 'src_bytes', 'dst_bytes', 'count',
    'same_srv_rate', 'diff_srv_rate', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_same_src_port_rate'
]

alert_counters = {
    "fire": [],
    "intrusion": []
}
last_email_sent_time = {
    "fire": 0,
    "intrusion": 0
}
COOLDOWN_SECONDS = 600  # 10 phút
ALERT_WINDOW_SECONDS = 60  # Lỗi liên tục trong 60 giây

def append_log(entry):
    log_file = "log.json"
    logs = []

    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []

    logs.append(entry)

    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)
  
# Load trạng thái từ file nếu có
def load_status():
    if os.path.exists("status.json"):
        with open("status.json", "r") as f:
            return json.load(f)

def save_status(data):
    with open("status.json", "w") as f:
        json.dump(data, f)


# Load từ file khi khởi động
current_status = load_status()

@app.route('/')
def home():
    return "Intrusion Detection AI Server is running!"

@app.route('/api/infer', methods=['POST'])
def infer_intrusion():
    try:
        data = request.json
        input_data = [data[feat] for feat in selected_features]
        input_array = np.array([input_data])
        pred = model.predict(input_array)[0]
        label = "Tấn công" if pred == 1 else "Bình thường"
        return jsonify({"status": "ok", "intrusion": label})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/status')
def status():
    return jsonify(current_status)

@app.route('/api/set_status', methods=['POST'])
def set_status():
    global current_status, user_email, last_email_sent_time, alert_counters
    data = request.json
    current_status.update(data)
    save_status(current_status) 
    now = time.time()
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")  
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fire": data.get("fire", False),
        "intrusion": data.get("intrusion", "Bình thường"),
        "temperature": data.get("temperature", 0.0),
        "humidity": data.get("humidity", 0.0)
    }
    append_log(log_entry)
    
    # FIRE LOGIC
    if data.get("fire"):
        alert_counters["fire"].append(now)
        # Giữ lại chỉ các sự kiện trong 60s gần nhất
        alert_counters["fire"] = [t for t in alert_counters["fire"] if now - t <= ALERT_WINDOW_SECONDS]

        if len(alert_counters["fire"]) >= 3 and now - last_email_sent_time["fire"] > COOLDOWN_SECONDS:
            if user_email:
                send_email_alert(
                    " Cảnh báo cháy nghiêm trọng",
                    f"Hệ thống phát hiện cháy liên tục tại {timestamp_str}.",
                    user_email
                )
                last_email_sent_time["fire"] = now
    else:
        alert_counters["fire"] = []  # reset nếu không còn lỗi

    # INTRUSION LOGIC
    if data.get("intrusion") != "Bình thường":
        alert_counters["intrusion"].append(now)
        alert_counters["intrusion"] = [t for t in alert_counters["intrusion"] if now - t <= ALERT_WINDOW_SECONDS]

        if len(alert_counters["intrusion"]) >= 3 and now - last_email_sent_time["intrusion"] > COOLDOWN_SECONDS:
            if user_email:
                send_email_alert(
                    " Cảnh báo xâm nhập mạng",
                    f"Phát hiện tấn công mạng liên tục tại {timestamp_str}.",
                    user_email
                )
                last_email_sent_time["intrusion"] = now
    else:
        alert_counters["intrusion"] = []

    return jsonify({"message": "Đã cập nhật dữ liệu", "data": current_status})



@app.route('/test')
def test():
    return "<h1> Flask server hoạt động trên LAN!</h1>"

@app.route('/api/logs')
def get_logs():
    log_file = "log.json"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try:
                logs = json.load(f)
                # Lấy 5 log mới nhất và đảo ngược để log mới nhất nằm đầu tiên
                latest_logs = logs[-5:][::-1]
                return jsonify({"logs": latest_logs})
            except:
                return jsonify({"logs": []})
    return jsonify({"logs": []})


@app.route('/api/clear_logs', methods=['POST'])
def clear_logs():
    with open("log.json", "w") as f:
        json.dump([], f)
    return jsonify({"message": "Đã xoá log thành công"})

user_email = None  # Biến toàn cục lưu email người dùng

@app.route('/api/set_email', methods=['POST'])
def set_email():
    global user_email
    data = request.json
    user_email = data.get("email")
    return jsonify({"message": "Đã lưu email người dùng", "email": user_email})

def send_warning_email(to_email, subject, message):
    admin_email = "22520216@gm.uit.edu.vn"
    admin_password = "vrvk setl tapc hnmx"

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = admin_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(admin_email, admin_password)
            smtp.send_message(msg)
            print(f"Đã gửi email cảnh báo đến {to_email}")
    except Exception as e:
        print(f"Lỗi gửi email: {e}")

if __name__ == '__main__':
    print(" Flask server started at http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
