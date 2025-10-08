/*
 * Arduino Sensor Reader for Autonomous Tracking Robot
 * 
 * Reads MPU6050 (accelerometer/gyro) and ultrasonic distance sensor
 * Sends data to Raspberry Pi via serial in JSON format
 * 
 * Hardware:
 * - MPU6050: I2C (SDA=A4, SCL=A5 on Arduino Uno)
 * - Ultrasonic Sensor: HC-SR04 (TRIG=7, ECHO=8)
 * 
 * Serial: 9600 baud
 * 
 * Install required library:
 * - Adafruit MPU6050 (Sketch → Include Library → Manage Libraries → search "Adafruit MPU6050")
 */

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

// Pin definitions for ultrasonic sensor
#define TRIG_PIN 7
#define ECHO_PIN 8

// Initialize MPU6050
Adafruit_MPU6050 mpu;

// Variables to store MPU6050 data
float accelX, accelY, accelZ;
float gyroX, gyroY, gyroZ;
float temperature;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Wait for serial to be ready
  delay(1000);
  
  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("{\"error\":\"MPU6050 not found\"}");
    while (1) {
      delay(1000);
    }
  }
  
  // Configure MPU6050
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  // Initialize ultrasonic sensor pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  Serial.println("{\"status\":\"Arduino Ready\"}");
  delay(1000);
}

void loop() {
  // Read MPU6050 sensor
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  // Store acceleration values (m/s²)
  accelX = a.acceleration.x;
  accelY = a.acceleration.y;
  accelZ = a.acceleration.z;
  
  // Store gyroscope values (rad/s)
  gyroX = g.gyro.x;
  gyroY = g.gyro.y;
  gyroZ = g.gyro.z;
  
  // Store temperature (°C)
  temperature = temp.temperature;
  
  // Read distance from ultrasonic sensor
  float distance = readUltrasonic();
  
  // Send data as JSON
  // Format: {"accelX":X,"accelY":Y,"accelZ":Z,"gyroX":X,"gyroY":Y,"gyroZ":Z,"temp":T,"dist":D}
  Serial.print("{\"accelX\":");
  Serial.print(accelX, 2);
  Serial.print(",\"accelY\":");
  Serial.print(accelY, 2);
  Serial.print(",\"accelZ\":");
  Serial.print(accelZ, 2);
  Serial.print(",\"gyroX\":");
  Serial.print(gyroX, 2);
  Serial.print(",\"gyroY\":");
  Serial.print(gyroY, 2);
  Serial.print(",\"gyroZ\":");
  Serial.print(gyroZ, 2);
  Serial.print(",\"temp\":");
  Serial.print(temperature, 1);
  Serial.print(",\"dist\":");
  Serial.print(distance, 1);
  Serial.println("}");
  
  // Update every 100ms (10 Hz)
  delay(100);
}

float readUltrasonic() {
  // Send trigger pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Read echo pulse
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);  // 30ms timeout
  
  // Calculate distance in cm (speed of sound = 343 m/s = 0.0343 cm/µs)
  // Distance = (duration / 2) * 0.0343
  float distance = (duration / 2.0) * 0.0343;
  
  // Return 0 if out of range or error
  if (distance <= 0 || distance > 400) {
    return 0;
  }
  
  return distance;
}
