/*
 * MPU6050 + HC-SR04 JSON streamer (Arduino Uno)
 * - I2C: SDA=A4, SCL=A5
 * - HC-SR04: TRIG=D7, ECHO=D8
 * - Serial: 9600 baud
 *
 * Libraries:
 *  - Adafruit MPU6050
 *  - Adafruit Unified Sensor
 *  - Adafruit BusIO
 */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MPU6050.h>

// Ultrasonic pins (change if needed)
#define TRIG_PIN 7
#define ECHO_PIN 8


Adafruit_MPU6050 mpu;

float duration,distance;

void setup() {
  Serial.begin(9600);
  delay(400);

  // Ultrasonic pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Try MPU6050 at 0x68 then 0x69
  if (!mpu.begin(0x68)) {
    if (!mpu.begin(0x69)) {
      Serial.println("{\"error\":\"MPU6050 not found (0x68/0x69)\"}");
      while (1) { delay(1000); }
    }
  }

  // Configure MPU6050
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("{\"status\":\"MPU6050 + Ultrasonic Ready\"}");
  delay(300);
}

void loop() {
  // Read MPU6050
  sensors_event_t a, g, t;
  mpu.getEvent(&a, &g, &t);

  // Read HC-SR04 (cm)
  float distCM = readUltrasonicCM();

  // Output JSON
  Serial.print("{\"accelX\":"); Serial.print(a.acceleration.x, 2);
  Serial.print(",\"accelY\":"); Serial.print(a.acceleration.y, 2);
  Serial.print(",\"accelZ\":"); Serial.print(a.acceleration.z, 2);
  Serial.print(",\"gyroX\":");  Serial.print(g.gyro.x, 2);
  Serial.print(",\"gyroY\":");  Serial.print(g.gyro.y, 2);
  Serial.print(",\"gyroZ\":");  Serial.print(g.gyro.z, 2);
  Serial.print(",\"tempC\":");  Serial.print(t.temperature, 1);
  Serial.print(",\"distCM\":"); Serial.print(distCM, 1);
  Serial.println("}");

  delay(50); // ~20 Hz - faster sensor updates
}

float readUltrasonicCM() {
  // Trigger pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  distance = (duration*.0343)/2;

  return distance;
}
