from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import json
import os

app = Flask(__name__)
CORS(app)

model = joblib.load("intrusion_model.pkl")
selected_features = [
    'protocol_type', 'flag', 'src_bytes', 'dst_bytes', 'count',
    'same_srv_rate', 'diff_srv_rate', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_same_src_port_rate'
]

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
    global current_status
    data = request.json
    current_status.update(data)
    save_status(current_status)   
    return jsonify({"message": "Đã cập nhật dữ liệu", "data": current_status})


@app.route('/test')
def test():
    return "<h1> Flask server hoạt động trên LAN!</h1>"

if __name__ == '__main__':
    print(" Flask server started at http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
