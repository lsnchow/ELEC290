/*
 * Arduino Sensor Reader for Batman Car
 * 
 * Reads gas sensor, temperature sensor, and ultrasonic distance sensor
 * Sends data to Raspberry Pi via serial in JSON format
 * 
 * Hardware:
 * - Gas Sensor: MQ-2/MQ-135 on analog pin A0
 * - Temperature Sensor: DHT11/DHT22 on digital pin 2
 * - Ultrasonic Sensor: HC-SR04 (TRIG=7, ECHO=8)
 * 
 * Serial: 9600 baud
 */

#include <DHT.h>

// Pin definitions
#define GAS_PIN A0
#define DHT_PIN 2
#define DHT_TYPE DHT11  // Change to DHT22 if using DHT22
#define TRIG_PIN 7
#define ECHO_PIN 8

// Initialize DHT sensor
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Initialize ultrasonic sensor pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Wait for serial to be ready
  delay(2000);
}

void loop() {
  // Read gas sensor (analog value 0-1023)
  int gasValue = analogRead(GAS_PIN);
  
  // Read temperature from DHT sensor
  float temperature = dht.readTemperature();
  
  // Read distance from ultrasonic sensor
  float distance = readUltrasonic();
  
  // Check if readings are valid
  if (isnan(temperature)) {
    temperature = 25.0;  // Default value if sensor fails
  }
  
  // Send data as JSON
  Serial.print("{\"gas\":");
  Serial.print(gasValue);
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
