/*
  Combined Sensor Reader
  Arduino UNO R4 WiFi
  Sensors: HC-SR04, Adafruit MPU6050, MQ-2, CCS811 (CJMCU-811)
*/



#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include "SparkFunCCS811.h"

#define TRIG_PIN 9
#define ECHO_PIN 10
#define MQ2_PIN A0
#define CCS811_ADDR 0x5A

// Objects
Adafruit_MPU6050 mpu;
CCS811 airSensor(CCS811_ADDR);

void setup() {
  Serial.begin(115200);
  Serial.println("Starting sensors...");

  // --- HC-SR04 ---
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // --- MQ-2 ---
  pinMode(MQ2_PIN, INPUT);

  // --- I2C ---
  Wire.begin();

  // --- MPU6050 ---
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip!");
    while (1) { delay(10); }
  }
  Serial.println("MPU6050 connected.");
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  // --- CCS811 ---
  if (!airSensor.begin()) {
    Serial.println("CCS811 not detected! Check wiring (VCC=3.3V, WAK=GND).");
  } else {
    Serial.println("CCS811 ready.");
  }

  Serial.println("All sensors initialized.\n");
  delay(1000);
}

void loop() {
  // ---- HC-SR04 ----
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = duration * 0.034 / 2;

  // ---- MQ-2 ----
  int mq2Value = analogRead(MQ2_PIN);

  // ---- MPU6050 ----
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // ---- CCS811 ----
  float co2 = -1, tvoc = -1;
  if (airSensor.dataAvailable()) {
    airSensor.readAlgorithmResults();
    co2 = airSensor.getCO2();
    tvoc = airSensor.getTVOC();
  }

  // ---- Serial Output ----
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

  delay(1000);
}
