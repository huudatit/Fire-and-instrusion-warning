#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define DHTPIN           4     
#define DHTTYPE          DHT22
#define FIRE_SENSOR_PIN  34   
#define LED1_PIN         27    
#define LED2_PIN         26    
#define BUTTON_PIN       23    


volatile bool inSpike       = false;
volatile bool modeChanged   = false;
volatile unsigned long lastISRTime = 0;


void IRAM_ATTR handleButton() {
  unsigned long now = millis();
  if (now - lastISRTime > 200) {
    inSpike       = !inSpike;
    modeChanged   = true;
    lastISRTime   = now;
  }
}

const char* ssid       = "Thanh Binh - VNPT";
const char* password   = "22112006";
const char* serverName = "http://192.168.1.10:5000/api/set_status";

DHT    dht(DHTPIN, DHTTYPE);
const int FIRE_THRESHOLD = 1500;

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

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(FIRE_SENSOR_PIN, INPUT);
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN),
                  handleButton,
                  FALLING);

  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, LOW);

  randomSeed(analogRead(0));

  // Kết nối WiFi
  WiFi.begin(ssid, password);
  Serial.print("Đang kết nối WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nĐã kết nối WiFi!");
}

void loop() {
  
  if (modeChanged) {
    //Serial.printf(">>> MODE: %s\n", inSpike ? "SPIKE" : "NORMAL");
    modeChanged = false;
  }

  // 1) Đọc/gán nhiệt độ & độ ẩm
  float temperature, humidity;
  if (inSpike) {
    temperature = random(700, 801) / 10.0;    
    humidity    = random(800, 1001) / 10.0;    
  } else {
    temperature = dht.readTemperature();
    humidity    = dht.readHumidity();
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("Lỗi đọc DHT22!");
      return;
    }
  }

  // 2) Đọc cảm biến lửa
  int fireRaw       = analogRead(FIRE_SENSOR_PIN);
  bool fireDetected = (fireRaw < FIRE_THRESHOLD);

  // 3) In kết quả
  Serial.printf("Nhiệt độ: %.1f °C | Độ ẩm: %.1f %% | Lửa: %d (%s)\n",
                temperature, humidity, fireRaw,
                fireDetected ? "Có" : "Không");

  // 4) Nháy LED nếu vượt ngưỡng
  if (temperature > 40.0 || fireDetected) {
    blinkLEDs(5, 200);
  }

  // 5) Gửi HTTP POST
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String payload = String("{") +
      "\"temperature\":" + String(temperature,1) + "," +
      "\"humidity\":"    + String(humidity,1)    + "," +
      "\"fireRaw\":"     + String(fireRaw)       + "," +
      "\"intrusion\":\"Bình thường\"," +
      "\"source\":\"esp\"" +
    "}";

    int code = http.POST(payload);
    Serial.printf("Gửi dữ liệu... HTTP code: %d | IP: %s\n",
                  code, WiFi.localIP().toString().c_str());
    http.end();
  } else {
    Serial.println("Mất kết nối WiFi!");
  }

  // Delay 3s giữa các lần gửi
  delay(3000);
}
