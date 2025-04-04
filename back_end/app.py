import csv
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

sensor_data = {
    "fire": False,
    "intrusion": "Bình thường",
    "temperature": 90.0,
    "humidity": 80.0
}

# Hàm lưu log vào CSV
def log_to_csv(data):
    with open('sensor_log.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data.get("fire"),
            data.get("intrusion"),
            data.get("temperature"),
            data.get("humidity")
        ])

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(sensor_data)

@app.route('/api/update', methods=['POST'])
def update_data():
    data = request.json
    sensor_data.update(data)
    log_to_csv(sensor_data)  # Ghi log mỗi khi có update
    print("🔄 Updated data & logged to CSV")
    return jsonify({"status": "success", "updated": sensor_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
