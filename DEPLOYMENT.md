# 🦇 BATMAN CAR - Deployment Guide

## Overview
This guide will help you deploy the full autonomous tracking robot car with Batman-themed UI.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MAC (YOUR COMPUTER)                    │
│  Web Browser → http://192.168.0.108:5000                │
│  - Batman-themed dark UI                                │
│  - Live YOLO v8 video feed                             │
│  - WASD controls / Auto-tracking mode                   │
│  - Real-time sensor graphs                             │
└─────────────────────────────────────────────────────────┘
                            ↕ WebSocket/HTTP
┌─────────────────────────────────────────────────────────┐
│                   RASPBERRY PI 5                         │
│  Flask-SocketIO Server (app.py)                         │
│  - YOLOv8 human detection                              │
│  - Motor control (L298N)                               │
│  - Auto-tracking algorithm                             │
│  - MJPEG video streaming                               │
└─────────────────────────────────────────────────────────┘
          ↕ USB Serial (9600 baud)           ↕ GPIO
┌──────────────────────────────┐    ┌──────────────────┐
│         ARDUINO              │    │   L298N DRIVER   │
│  - Gas sensor (MQ-2/135)     │    │  - Motor 1       │
│  - Temperature (DHT11/22)    │    │  - Motor 2       │
│  - Distance (HC-SR04)        │    │                  │
└──────────────────────────────┘    └──────────────────┘
```

## Hardware Setup

### 1. L298N Motor Driver to Raspberry Pi 5

| L298N Pin | RPi GPIO | BCM Pin |
|-----------|----------|---------|
| ENA       | GPIO 17  | Pin 11  |
| IN1       | GPIO 27  | Pin 13  |
| IN2       | GPIO 22  | Pin 15  |
| ENB       | GPIO 18  | Pin 12  |
| IN3       | GPIO 23  | Pin 16  |
| IN4       | GPIO 24  | Pin 18  |
| GND       | GND      | Pin 6   |

**Power:**
- L298N 12V input: Connect to battery pack (7-12V)
- L298N 5V output: Can power Pi if sufficient current (NOT RECOMMENDED)
- Use separate 5V/3A power supply for Pi

### 2. Arduino Sensor Connections

**Gas Sensor (MQ-2/MQ-135):**
- VCC → 5V
- GND → GND
- A0 → Arduino A0

**Temperature Sensor (DHT11/DHT22):**
- VCC → 5V
- GND → GND
- DATA → Arduino Pin 2
- 10kΩ pull-up resistor between VCC and DATA (if needed)

**Ultrasonic Sensor (HC-SR04):**
- VCC → 5V
- GND → GND
- TRIG → Arduino Pin 7
- ECHO → Arduino Pin 8

### 3. Arduino to Raspberry Pi
- Connect Arduino USB cable to any Pi USB port
- Arduino will appear as `/dev/ttyUSB0` or `/dev/ttyACM0`

### 4. Camera
- Connect USB webcam to Pi USB port
- Will auto-detect at startup

## Software Deployment

### Step 1: Update Raspberry Pi Code

```bash
# SSH into your Pi
ssh raspberry@192.168.0.108

# Navigate to project
cd /path/to/ELEC290-src

# Pull latest changes
git pull origin main

# Install new dependencies
pip install Flask-SocketIO pyserial
```

### Step 2: Upload Arduino Sketch

1. Open `arduino_sensors.ino` in Arduino IDE
2. Select your Arduino board (Tools → Board)
3. Select correct port (Tools → Port → /dev/ttyUSB0 or similar)
4. **Important:** Adjust sensor pins in code if your wiring differs:
   - DHT_TYPE: Change to DHT22 if using DHT22 instead of DHT11
   - Pin numbers: Update if your wiring is different
5. Click Upload button
6. Open Serial Monitor (Tools → Serial Monitor)
7. Set baud rate to 9600
8. Verify JSON output: `{"gas":450,"temp":25.5,"dist":10.2}`

### Step 3: Test Individual Components

**Test Motors (without Arduino):**
```bash
python3 << 'EOF'
from motors import MotorController
import time

motors = MotorController()
print("Testing forward...")
motors.forward(50)
time.sleep(2)
print("Testing stop...")
motors.stop()
motors.cleanup()
EOF
```

**Test Arduino Serial:**
```bash
python3 << 'EOF'
from arduino_serial import ArduinoSerial
import time

arduino = ArduinoSerial()
for _ in range(10):
    data = arduino.get_data()
    print(data)
    time.sleep(1)
arduino.stop()
EOF
```

**Test YOLO Detection:**
```bash
python3 << 'EOF'
from detector import HumanDetector
import cv2

detector = HumanDetector()
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    results = detector.detect_humans(frame)
    print(f"Detected {len(results)} people")
cap.release()
EOF
```

### Step 4: Run Full System

```bash
# Ensure you're in the project directory
cd /path/to/ELEC290-src

# Run the app
python3 app.py
```

Expected output:
```
======================================================================
🦇 AUTONOMOUS TRACKING ROBOT CAR - ONLINE 🦇
======================================================================
Server: http://0.0.0.0:5000
Access from your Mac: http://<raspberry-pi-ip>:5000
Mode: MANUAL
======================================================================

YOLOv8n model loaded successfully
Camera detected at index 0
Motors initialized in DUMMY mode (no GPIO available)
Arduino serial: Attempting connection to /dev/ttyUSB0...
Arduino connected on /dev/ttyUSB0
PersonTracker initialized
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.0.108:5000
```

### Step 5: Access Web Interface

**From your Mac:**
1. Open browser
2. Go to `http://192.168.0.108:5000`
3. You should see the Batman-themed interface!

**If connection fails, use SSH tunnel:**
```bash
# On your Mac
ssh -L 5000:localhost:5000 raspberry@192.168.0.108

# Then access http://localhost:5000 in browser
```

## Using the System

### Manual Control Mode
1. Click **"Manual"** button (should be selected by default)
2. Use **WASD** keys on keyboard:
   - **W** = Forward
   - **A** = Turn Left
   - **S** = Backward
   - **D** = Turn Right
   - Release key to stop
3. Or click the on-screen buttons

### Auto-Tracking Mode
1. Click **"Auto Track"** button
2. Robot will:
   - Scan for humans using YOLO v8
   - Follow the largest detected person
   - Stop if person is closer than 8cm (distance sensor)
   - Stop if person is lost for more than 3 seconds
3. Switch back to Manual to regain control

### Emergency Stop
- Click **"⚠️ EMERGENCY STOP"** button at any time
- Immediately stops all motors
- Switches to Manual mode

## Features

### Live Video Feed
- MJPEG stream with YOLO detection boxes
- Displays FPS, detection count, and current mode
- Golden border matching Batman theme

### Sensor Graphs
- **Temperature**: Live line chart (golden line on dark background)
- Shows last 30 data points
- Auto-scales Y-axis
- Updates every second

### Real-Time Data
- Gas level (ppm)
- Temperature (°C)
- Distance (cm)
- Motor direction and speed
- Arduino connection status
- Tracking status

## Troubleshooting

### Motor Issues
**Problem:** Motors don't work or only one motor works
- Check wiring to L298N
- Verify GPIO pins match config.py
- Ensure L298N has power (12V input)
- Check motor connections to L298N output

**Problem:** "DUMMY mode" message
- GPIO library not available
- Means motors won't actually move (for testing)
- Install gpiod: `pip install gpiod`

### Arduino Issues
**Problem:** "Arduino: DISCONNECTED" in UI
- Check USB cable connection
- Verify Arduino sketch uploaded correctly
- Check serial port in config.py (ARDUINO_PORT)
- Test: `ls /dev/ttyUSB* /dev/ttyACM*`

**Problem:** Sensor readings show "--"
- Arduino not sending data
- Open Serial Monitor in Arduino IDE to verify output
- Check sensor wiring
- Verify baud rate is 9600

### Camera Issues
**Problem:** Video feed shows black or "No camera found"
- Try different USB port
- Check: `ls /dev/video*`
- Test: `v4l2-ctl --list-devices`
- Unplug/replug camera

### Network Issues
**Problem:** Can't access from Mac
- Verify Pi IP: `hostname -I` on Pi
- Check firewall on Mac
- Use SSH tunnel as backup
- Ensure both devices on same network

### YOLO Performance
**Problem:** Very slow/laggy video
- Already optimized (256px inference, frame skipping)
- Close other programs on Pi
- Reduce CAMERA_WIDTH/HEIGHT in config.py
- Increase PROCESS_EVERY_N_FRAMES in config.py

## Configuration

Edit `config.py` to adjust:

```python
# Camera settings
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
CAMERA_FPS = 15

# YOLO settings
IMGSZ = 256  # Inference size (lower = faster)
PROCESS_EVERY_N_FRAMES = 3  # Process every Nth frame

# Motor settings
DEFAULT_SPEED = 60  # 0-100
TURN_SPEED = 50

# Tracking settings
STOP_DISTANCE = 8  # cm - stop if closer than this
PERSON_LOST_TIMEOUT = 3  # seconds

# Arduino settings
ARDUINO_PORT = '/dev/ttyUSB0'  # Or '/dev/ttyACM0'
ARDUINO_BAUD = 9600
```

## Safety Tips

1. **Start in Manual Mode**: Test motors before enabling auto-tracking
2. **Clear Space**: Ensure area is clear of obstacles
3. **Emergency Stop Ready**: Know where the button is
4. **Battery Level**: Monitor battery to avoid brownouts
5. **Distance Sensor**: Ensure ultrasonic sensor is working to prevent collisions
6. **Supervision**: Don't leave robot running unattended

## Next Steps

1. **Calibrate Motors**: Adjust speed values for your specific motors
2. **Tune Tracking**: Modify tracking algorithm in `tracking.py`
3. **Add Features**: 
   - Voice control
   - Path recording/playback
   - Obstacle avoidance
   - Multiple person tracking
4. **Improve UI**: Add more graphs, settings panel, etc.

## File Structure

```
ELEC290-src/
├── app.py                 # Main Flask server
├── detector.py            # YOLO detection
├── motors.py              # L298N motor control
├── arduino_serial.py      # Arduino communication
├── tracking.py            # Auto-tracking algorithm
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── arduino_sensors.ino    # Arduino sketch
├── templates/
│   └── index.html         # Batman UI
├── README.md              # Original docs
├── WIRING.md              # Wiring diagrams
├── IMPLEMENTATION_PLAN.md # Feature roadmap
└── DEPLOYMENT.md          # This file
```

## Support

If you encounter issues:
1. Check error messages in terminal
2. Verify all connections
3. Test components individually
4. Check config.py settings
5. Review logs and status in web UI

---

**🦇 Made with ❤️ for ELEC290 🦇**
