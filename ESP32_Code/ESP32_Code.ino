#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT11

#define FIRE_SENSOR_PIN 34

#define LED1_PIN 27     // Đèn LED 1
#define LED2_PIN 26    // Đèn LED 2

const char* ssid = "Test ESP32";
const char* password = "12345678";

const char* serverName = "http://192.168.215.139:5000/api/set_status";
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(FIRE_SENSOR_PIN, INPUT);
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);

  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, LOW);

  WiFi.begin(ssid, password);
  Serial.print("Đang kết nối WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nĐã kết nối WiFi!");
}

void blinkLEDs(int times, int interval_ms) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED1_PIN, HIGH);
    digitalWrite(LED2_PIN, HIGH);
    delay(interval_ms);
    digitalWrite(LED1_PIN, LOW);
    digitalWrite(LED2_PIN, LOW);
    delay(interval_ms);
  }
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int fireRaw = analogRead(FIRE_SENSOR_PIN);
  bool fireDetected = fireRaw < 1500; // điều chỉnh ngưỡng nếu cần

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Lỗi đọc cảm biến DHT11");
    return;
  }

  Serial.printf("Nhiệt độ: %.1f °C | Độ ẩm: %.1f %% | Lửa: %s\n",
                temperature, humidity, fireDetected ? "Có" : "Không");

  // Nếu vượt ngưỡng nhiệt độ hoặc có lửa → nháy LED
  if (temperature > 40.0 || fireDetected) {
    blinkLEDs(5, 200); // nháy 5 lần, mỗi lần 200ms
  }

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"temperature\":" + String(temperature, 1)
                   + ",\"humidity\":" + String(humidity, 1)
                   + ",\"fire\":" + String(fireDetected ? "true" : "false")
                   + ",\"intrusion\":\"Bình thường\""
                   + ",\"source\":\"esp\"}";

    int httpResponseCode = http.POST(jsonPayload);
    Serial.printf("Gửi dữ liệu... Phản hồi: %d\n", httpResponseCode);
    Serial.print("Địa chỉ IP của ESP: ");
    Serial.printf("Giá trị cảm biến lửa (raw): %d\n", fireRaw);
    Serial.println(WiFi.localIP());
    http.end();
  } else {
    Serial.println("Mất kết nối WiFi!");
  }
  delay(3000); // Gửi mỗi 3s
}
