/*
  Combined Sensor Reader - JSON Output
  Arduino UNO R4 WiFi
  Sensors: HC-SR04, Adafruit MPU6050, MQ-2, CCS811 (CJMCU-811)
  
  Pin Configuration:
  - HC-SR04: TRIG=D9, ECHO=D10
  - MQ-2: A0
  - MPU6050: I2C (SDA=A4, SCL=A5)
  - CCS811: I2C (SDA=A4, SCL=A5, ADDR=0x5A)
  
  Output: JSON at 115200 baud, ~20 Hz
*/

#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include "SparkFunCCS811.h"

#define TRIG_PIN 9
#define ECHO_PIN 10
#define MQ2_PIN A0
#define CCS811_ADDR 0x5A

// Sensor objects
Adafruit_MPU6050 mpu;
CCS811 airSensor(CCS811_ADDR);

void setup() {
  Serial.begin(115200);
  delay(500);

  // --- HC-SR04 ---
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // --- MQ-2 ---
  pinMode(MQ2_PIN, INPUT);

  // --- I2C ---
  Wire.begin();

  // --- MPU6050 ---
  if (!mpu.begin()) {
    Serial.println("{\"error\":\"MPU6050 not found\"}");
    while (1) { delay(1000); }
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  // --- CCS811 ---
  if (!airSensor.begin()) {
    Serial.println("{\"warning\":\"CCS811 not detected, air quality disabled\"}");
  }

  Serial.println("{\"status\":\"All sensors ready\"}");
  delay(500);
}

void loop() {
  // ---- HC-SR04 Distance ----
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout
  float distance = (duration > 0) ? (duration * 0.034 / 2) : 999;

  // ---- MQ-2 Gas Sensor ----
  int mq2Value = analogRead(MQ2_PIN);

  // ---- MPU6050 ----
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // ---- CCS811 Air Quality ----
  float co2 = -1, tvoc = -1;
  if (airSensor.dataAvailable()) {
    airSensor.readAlgorithmResults();
    co2 = airSensor.getCO2();
    tvoc = airSensor.getTVOC();
  }

  // ---- JSON Output ----
  Serial.print("{\"distCM\":");
  Serial.print(distance, 1);
  
  Serial.print(",\"mq2\":");
  Serial.print(mq2Value);
  
  Serial.print(",\"accelX\":");
  Serial.print(a.acceleration.x, 2);
  Serial.print(",\"accelY\":");
  Serial.print(a.acceleration.y, 2);
  Serial.print(",\"accelZ\":");
  Serial.print(a.acceleration.z, 2);
  
  Serial.print(",\"gyroX\":");
  Serial.print(g.gyro.x, 2);
  Serial.print(",\"gyroY\":");
  Serial.print(g.gyro.y, 2);
  Serial.print(",\"gyroZ\":");
  Serial.print(g.gyro.z, 2);
  
  Serial.print(",\"tempC\":");
  Serial.print(temp.temperature, 1);
  
  Serial.print(",\"co2\":");
  Serial.print(co2, 0);
  Serial.print(",\"tvoc\":");
  Serial.print(tvoc, 0);
  
  Serial.println("}");

  delay(50); // ~20 Hz update rate
}
