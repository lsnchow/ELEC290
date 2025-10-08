/*
 * Simple Arduino Serial Test
 * 
 * This is a minimal test sketch to verify serial communication works.
 * Upload this first to rule out sensor issues.
 * 
 * Expected output every second:
 * {"gas":123,"temp":25.5,"dist":10.0}
 */

void setup() {
  // Initialize serial at 9600 baud
  Serial.begin(9600);
  
  // Wait for serial to be ready
  delay(2000);
  
  // Send a startup message
  Serial.println("{\"status\":\"Arduino Ready\"}");
}

void loop() {
  // Send fake sensor data (no sensors required!)
  Serial.print("{\"gas\":");
  Serial.print(random(300, 600));  // Random gas value
  Serial.print(",\"temp\":");
  Serial.print(random(20, 30));    // Random temperature
  Serial.print(",\"dist\":");
  Serial.print(random(5, 50));     // Random distance
  Serial.println("}");
  
  // Send every 1 second
  delay(1000);
}
