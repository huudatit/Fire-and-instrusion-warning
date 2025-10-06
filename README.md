# Fire-and-instrusion-warning
This project develops an integrated monitoring system to enhance both physical security (fire safety) and cybersecurity (network defense) in an Internet of Things (IoT) environment. The system performs two main functions:

Fire Incident Detection: Monitoring the environment using data from physical sensors (temperature, humidity, fire, etc.).

Network Intrusion Detection (NIDS): Analyzing network traffic (specifically abnormal attacks like DoS, DDoS) using Machine Learning (ML) models.

The system provides a user-friendly Web Interface (GUI) to display real-time monitoring information and automatically sends email alerts upon detecting an incident.

Core Technologies
Component	Technology/Technique	Details
IoT Device	ESP32	collects sensor data (temperature, humidity, fire) and sends it to the backend server via HTTP POST.
Backend Server	Flask (Python)	Handles data processing, loads the AI model, and deploys the API.
Frontend Web	Vue.js	builds the User Interface (GUI) to display system status and alerts in real-time.
AI Models	Machine Learning (SL)	utilizes Logistic Regression (LR), K-Nearest Neighbors (KNN), and Decision Tree (DT) algorithms for network intrusion classification.
Database	Firebase Realtime Database	Stores and manages user login information.
Packet Capture	Scapy (Python)	Used to capture network packets, extract features, and feed them into the AI model for classification.
Basic Structure
The project operates in the main flow: IoT Device → Sends data via Flask API → Server processes with AI and Database → Displays on the Web Interface and sends Email Alerts.

1. Installation (Inference)
Backend: Requires Python, Flask, ML/AI libraries (like Scikit-learn, Optuna), and the packet capture library Scapy.

Frontend: Requires the Node.js environment and Vue.js dependencies.

Device: Programming for the ESP32 to connect to WiFi and send sensor data (DHT11, flame sensor) to the Flask server's IP address.

2. Operation (Inference)
Start the Backend Server (Flask).

Run the Monitor.py program to monitor network traffic on a selected interface.

Start the Frontend Web App and access the interface via a browser.

Power on the ESP32 device to begin sending sensor data to the server.
