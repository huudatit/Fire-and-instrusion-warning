from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import random  # 👈 Thêm để giả lập thay đổi

app = Flask(__name__)
CORS(app)

model = joblib.load("intrusion_model.pkl")
selected_features = [
    'protocol_type', 'flag', 'src_bytes', 'dst_bytes', 'count',
    'same_srv_rate', 'diff_srv_rate', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_same_src_port_rate'
]

@app.route('/')
def home():
    return "🔥 Intrusion Detection AI Server is running!"

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

# ✅ Route này sẽ được frontend gọi liên tục
@app.route('/api/status')
def status():
    # 👇 Giả lập dữ liệu thay đổi mỗi lần gọi
    fire = random.choice([True, False])
    intrusion = random.choice(["Bình thường", "Tấn công DDoS", "Tấn công R2L", "Tấn công Probe"])
    temp = round(random.uniform(28, 65), 1)
    hum = round(random.uniform(30, 90), 1)
    return jsonify({
        "fire": fire,
        "intrusion": intrusion,
        "temperature": temp,
        "humidity": hum
    })

@app.route('/test')
def test():
    return "<h1>✅ Flask server hoạt động trên LAN!</h1>"

if __name__ == '__main__':
    print("✅ Flask server started at http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
