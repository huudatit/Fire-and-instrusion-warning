from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np

app = Flask(__name__)
CORS(app)


# Load AI model
model = joblib.load("intrusion_model.pkl")
selected_features = [
    'protocol_type', 'flag', 'src_bytes', 'dst_bytes', 'count',
    'same_srv_rate', 'diff_srv_rate', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_same_src_port_rate'
]


# Biến lưu trạng thái hiện tại để frontend có thể hiển thị
current_status = {
    "fire": False,
    "intrusion": "Bình thường",
    "temperature": 30.0,
    "humidity": 50.0
}

@app.route('/')
def home():
    return " Intrusion Detection AI Server is running!"

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


# API frontend gọi mỗi 3s để lấy dữ liệu hiển thị
@app.route('/api/status')
def status():
    return jsonify(current_status)

# API này cho phép giả lập dữ liệu từ trang admin
@app.route('/api/set_status', methods=['POST'])
def set_status():
    global current_status
    data = request.json
    current_status.update(data)
    return jsonify({"message": "Đã cập nhật dữ liệu giả lập", "data": current_status})


@app.route('/test')
def test():
    return "<h1> Flask server hoạt động trên LAN!</h1>"

if __name__ == '__main__':
    print(" Flask server started at http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
