#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define DHTPIN 4          // Chân kết nối DHT11
#define DHTTYPE DHT11

#define FIRE_SENSOR_PIN 34  // Nếu là analog, chọn chân ADC

const char* ssid = "Cloud Coffee 2";
const char* password = "23456789";

const char* serverName = "http://192.168.61.68:5000/api/set_status";

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(FIRE_SENSOR_PIN, INPUT);

  WiFi.begin(ssid, password);
  Serial.print("Đang kết nối WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n Đã kết nối WiFi!");
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int fireRaw = analogRead(FIRE_SENSOR_PIN);
  bool fireDetected = fireRaw < 1000; // Ngưỡng tuỳ theo cảm biến bạn

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println(" Lỗi đọc cảm biến DHT11");
    return;
  }

  Serial.printf(" Nhiệt độ: %.1f °C |  Độ ẩm: %.1f %% |  Lửa: %s\n",
                temperature, humidity, fireDetected ? "Có" : "Không");

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"temperature\":" + String(temperature, 1)
                       + ",\"humidity\":" + String(humidity, 1)
                       + ",\"fire\":" + String(fireDetected ? "true" : "false") + "}";

    int httpResponseCode = http.POST(jsonPayload);
    Serial.printf(" Gửi dữ liệu... Phản hồi: %d\n", httpResponseCode);
    http.end();
  } else {
    Serial.println(" Mất kết nối WiFi!");
  }

  delay(5000); // Gửi mỗi 5s
}
