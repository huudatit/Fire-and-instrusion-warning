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
fire_model = joblib.load("random_forest_fire_model.pkl")
humidity_spike_model = joblib.load("random_forest_humidity_spike_model.pkl")

selected_features = [
    'protocol_type', 'flag', 'src_bytes', 'dst_bytes', 'count',
    'same_srv_rate', 'diff_srv_rate', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_same_src_port_rate'
]
user_email = None
alert_counters = {
    "fire": [],
    "intrusion": []
}
last_email_sent_time = {
    "fire": 0,
    "intrusion": 0
}
COOLDOWN_SECONDS = 10 # Thời gian chờ tối thiểu giữa 2 email
ALERT_WINDOW_SECONDS = 3  # Sự kiện trong vòng 60 giây


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
    global current_status, user_email, last_email_sent_time
    data = request.json

    # Chỉ cập nhật nếu source là ESP
    if data.get("source") in ["esp", "monitor"]:
        
        temperature = data.get("temperature", 0.0)
        humidity = data.get("humidity", 0.0)
        intrusion = data.get("intrusion", "Bình thường")

        
        fire_raw = data.get("fireRaw", 2000)

        
        fire_input = np.array([[temperature, fire_raw]])
        fire_pred = fire_model.predict(fire_input)[0]
        fire_detected = bool(fire_pred)

        humidity_input = np.array([[humidity]])
        humidity_spike_pred = humidity_spike_model.predict(humidity_input)[0]
        humidity_spike = bool(humidity_spike_pred)

        current_status.update({
            "temperature": temperature,
            "humidity": humidity,
            "fire": fire_detected,
            "intrusion": intrusion,
            "humidity_spike": humidity_spike 
        })

        save_status(current_status)


        now = time.time()
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp_str,
            "fire": current_status["fire"],
            "intrusion": current_status["intrusion"],
            "temperature": current_status["temperature"],
            "humidity": current_status["humidity"]
        }
        append_log(log_entry)

        # Gửi email nếu có cảnh báo
        if current_status["fire"] and user_email:
            if now - last_email_sent_time["fire"] > COOLDOWN_SECONDS:
                message = f"""
          Cảnh báo cháy tại {timestamp_str}:

          Lửa: Có
          Tấn công mạng: {current_status["intrusion"]}
          Nhiệt độ: {current_status["temperature"]} °C
          Độ ẩm: {current_status["humidity"]} %
        """
                send_email_alert("Cảnh báo cháy", message, user_email)
                last_email_sent_time["fire"] = now

        if current_status["intrusion"] != "Bình thường" and user_email:
            if now - last_email_sent_time["intrusion"] > COOLDOWN_SECONDS:
                message = f"""
            Cảnh báo xâm nhập mạng tại {timestamp_str}:

            Lửa: {"Có" if current_status["fire"] else "Không"}
            Tấn công mạng: {current_status["intrusion"]}
            Nhiệt độ: {current_status["temperature"]} °C
            Độ ẩm: {current_status["humidity"]} %
        """
                send_email_alert("Cảnh báo xâm nhập mạng", message, user_email)
                last_email_sent_time["intrusion"] = now


    return jsonify({"message": "Đã xử lý dữ liệu", "data": current_status})


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
@app.route('/api/esp_update', methods=['POST'])
def esp_update():
    global current_status
    data = request.json
    current_status.update(data)
    save_status(current_status)
    # Ghi log thực sự
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fire": data.get("fire", False),
        "intrusion": data.get("intrusion", "Bình thường"),
        "temperature": data.get("temperature", 0.0),
        "humidity": data.get("humidity", 0.0)
    }
    append_log(log_entry)
    return jsonify({"message": "ESP cập nhật thành công"})

@app.route('/api/set_email', methods=['POST'])
def set_email():
    global user_email
    data = request.json
    user_email = data.get("email")
    print("Email đã nhận và lưu:", user_email) # thêm log
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

def send_email_alert(subject, message, to_email):
    send_warning_email(to_email, subject, message)


@app.route('/api/send_email_now', methods=['POST'])
def send_email_now():
    global user_email
    if not user_email:
        return jsonify({"message": "Chưa có email người dùng"}), 400

    # Lấy trạng thái hiện tại từ current_status
    status = current_status
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    message = f"""
    Tình trạng hệ thống tại {timestamp}:
     Lửa: {"Có" if status.get("fire") else "Không"}
     Xâm nhập mạng: {status.get("intrusion")}
     Nhiệt độ: {status.get("temperature")} °C
     Độ ẩm: {status.get("humidity")} %
    """

    subject = " Báo cáo thủ công từ hệ thống giám sát IoT"
    send_warning_email(user_email, subject, message)
    return jsonify({"message": "Đã gửi email thành công"}), 200

if __name__ == '__main__':
    print(" Flask server started at http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
