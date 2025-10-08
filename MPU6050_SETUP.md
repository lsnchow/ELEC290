# MPU6050 Setup Guide

## Hardware Configuration

Your Arduino now uses:
- ✅ **MPU6050** (accelerometer + gyroscope + temperature)
- ✅ **HC-SR04** ultrasonic sensor
- ❌ No gas sensor (MQ-2/MQ-135)
- ❌ No DHT temperature sensor

## Arduino Wiring

### MPU6050 (I2C)
- **VCC** → Arduino 5V
- **GND** → Arduino GND
- **SDA** → Arduino A4 (on Uno/Nano)
- **SCL** → Arduino A5 (on Uno/Nano)

### HC-SR04 Ultrasonic
- **VCC** → Arduino 5V
- **GND** → Arduino GND
- **TRIG** → Arduino Pin 7
- **ECHO** → Arduino Pin 8

## Arduino Library Installation

You need to install the **Adafruit MPU6050** library:

1. Open Arduino IDE
2. Go to **Sketch** → **Include Library** → **Manage Libraries**
3. Search for "**Adafruit MPU6050**"
4. Install **Adafruit MPU6050** (will also install dependencies: Adafruit Unified Sensor, Adafruit BusIO)
5. Click **Install All** when prompted

## Upload Sketch

1. Open `arduino_sensors.ino` in Arduino IDE
2. Select your board (e.g., Arduino Uno)
3. Select the correct port (e.g., `/dev/ttyUSB0` or `/dev/ttyACM0`)
4. Click **Upload**

## Verify Communication

### Test in Arduino Serial Monitor:
1. Open **Tools** → **Serial Monitor**
2. Set baud rate to **9600**
3. You should see JSON output every 100ms:
```json
{"accelX":0.12,"accelY":-0.05,"accelZ":9.81,"gyroX":0.01,"gyroY":-0.02,"gyroZ":0.00,"temp":24.5,"dist":15.3}
```

### Sensor Data Explained:
- **accelX, accelY, accelZ**: Acceleration in m/s² (expect ~9.8 on Z-axis due to gravity)
- **gyroX, gyroY, gyroZ**: Rotation rate in rad/s (should be ~0 when stationary)
- **temp**: Temperature from MPU6050 in °C
- **dist**: Distance from ultrasonic sensor in cm

## Troubleshooting

### "MPU6050 not found" Error
**Symptom**: Serial Monitor shows `{"error":"MPU6050 not found"}`

**Solutions**:
1. Check I2C wiring (SDA→A4, SCL→A5)
2. Try different I2C address (MPU6050 can be 0x68 or 0x69)
3. Check if MPU6050 has power (LED should light up)
4. Run I2C scanner sketch to detect address

### Noisy Readings
**Symptom**: Accelerometer/gyro values jump around wildly

**Solutions**:
1. MPU6050 is very sensitive - this is normal
2. Values stabilize when stationary
3. Can add filtering in code if needed (moving average, Kalman filter)

### No Serial Data in Python
**Symptom**: Arduino powered but Python shows "Arduino not connected"

**Solutions**:
1. **Close Arduino IDE Serial Monitor** (it locks the port)
2. Check port in `config.py` (try `/dev/ttyUSB0` or `/dev/ttyACM0`)
3. Run `python3 debug_arduino.py` to diagnose
4. Git pull latest code (has auto-port detection)

## Web UI Changes

The web interface now shows:
- **MPU6050 Accelerometer**: 3 values (X, Y, Z in m/s²)
- **MPU6050 Gyroscope**: 3 values (X, Y, Z in rad/s)
- **Other Sensors**: Temperature (°C) and Distance (cm)

## Using the Data

### Detecting Movement
- Monitor gyro values - any rotation will show up
- Useful for detecting if robot is turning

### Detecting Collisions/Bumps
- Monitor accel values - sudden spikes indicate impact
- Can use as collision detection

### Tilt Sensing
- Gravity always pulls at 9.8 m/s²
- If Z-axis shows 9.8 → robot is level
- If X or Y show high values → robot is tilted

## Next Steps

After uploading:
1. Close Arduino Serial Monitor
2. Git pull on Raspberry Pi: `cd ~/robot && git pull`
3. Restart app: `python3 app.py`
4. Check web UI at `http://192.168.0.108:5000`

You should now see real MPU6050 data updating in the web interface!
