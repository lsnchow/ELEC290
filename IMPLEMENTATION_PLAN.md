# Autonomous Tracking Robot Car - Implementation Plan

## Overview
Building a robot car with autonomous person-tracking AND manual control modes.

## Hardware Components
1. **Raspberry Pi 5** - Main controller
2. **USB Webcam** - YOLOv8 human detection
3. **L298N Motor Driver** - Controls 2 DC motors
4. **HC-SR04 Ultrasonic Sensor** - Collision avoidance (on Pi)
5. **Arduino** - Secondary sensor hub
   - Gas sensor
   - Temperature sensor  
   - Distance sensor
6. **2x DC Motors** - Left/Right wheels

## Features to Implement

### 1. Motor Control (`motors.py`) ✅ CREATED
- L298N motor driver interface
- Forward, backward, left, right, stop
- Speed control (PWM)

### 2. Arduino Serial Communication (`arduino_serial.py`) ✅ CREATED
- Read gas, temperature, distance from Arduino
- JSON or CSV format
- Background thread for continuous reading

### 3. Auto-Tracking Mode (`tracking.py`) - TO CREATE
- Detect humans with YOLOv8
- Calculate center of bounding box
- Adjust motors to follow person
- Stop if ultrasonic distance < 8cm
- Safety: timeout if person lost

### 4. Manual Control Mode (WebSocket in `app.py`) - TO UPDATE
- WASD keyboard control
- Real-time bidirectional communication
- Override auto-tracking

### 5. Enhanced Frontend (`templates/index.html`) - TO UPDATE
- **Batman-themed dark UI** (black/dark gray, yellow accents)
- Live MJPEG video feed with YOLOv8 detections
- Real-time graphs (Recharts.js):
  - Temperature over time
  - Gas levels over time
  - Distance readings
- Control panel:
  - Mode switch: Auto/Manual
  - WASD controls (manual mode)
  - Emergency stop button
- Status indicators:
  - Motor status
  - Sensor readings
  - Detection count
  - System FPS

### 6. Backend Updates (`app.py`) - TO UPDATE
- WebSocket support (Flask-SocketIO)
- Routes for sensor data streaming
- Mode switching (auto/manual)
- Integration of all modules

## GPIO Pin Assignments

### Raspberry Pi 5
```
L298N Motor Driver:
- ENA (Motor A PWM): GPIO 17 (Pin 11)
- IN1 (Motor A Dir 1): GPIO 27 (Pin 13)
- IN2 (Motor A Dir 2): GPIO 22 (Pin 15)
- ENB (Motor B PWM): GPIO 18 (Pin 12)
- IN3 (Motor B Dir 1): GPIO 23 (Pin 16)
- IN4 (Motor B Dir 2): GPIO 24 (Pin 18)

HC-SR04 Ultrasonic (existing):
- TRIG: GPIO 23 (Pin 16) - CONFLICT! NEED TO CHANGE
- ECHO: GPIO 24 (Pin 18) - CONFLICT! NEED TO CHANGE

⚠️ PIN CONFLICT DETECTED - Need to reassign ultrasonic sensor!

New Ultrasonic Assignment:
- TRIG: GPIO 5 (Pin 29)
- ECHO: GPIO 6 (Pin 31) with voltage divider
```

### Arduino (Serial via USB)
- Connect to Pi via USB
- Port: `/dev/ttyUSB0` or `/dev/ttyACM0`
- Sends JSON: `{"gas":450,"temp":25.5,"dist":10.2}`

## File Structure
```
ELEC290-src/
├── app.py              # Main Flask app (TO UPDATE)
├── detector.py         # YOLOv8 detection (existing, ✅)
├── ultrasonic.py       # HC-SR04 sensor (TO UPDATE - fix pins)
├── motors.py           # L298N motor control (✅ CREATED)
├── arduino_serial.py   # Arduino communication (✅ CREATED)
├── tracking.py         # Auto-tracking logic (TO CREATE)
├── config.py           # Configuration (TO UPDATE)
├── requirements.txt    # Dependencies (TO UPDATE)
├── templates/
│   └── index.html      # Batman UI (TO CREATE NEW)
└── static/
    ├── css/
    │   └── batman.css  # Batman theme (TO CREATE)
    └── js/
        └── control.js  # WebSocket & controls (TO CREATE)
```

## Implementation Steps

### Phase 1: Core Modules ✅
- [x] Motor controller
- [x] Arduino serial reader

### Phase 2: Auto-Tracking (NEXT)
- [ ] Fix ultrasonic pin conflicts
- [ ] Create tracking logic
- [ ] Implement person-following algorithm
- [ ] Add safety (stop at 8cm)

### Phase 3: WebSocket & Manual Control
- [ ] Add Flask-SocketIO
- [ ] Implement WASD control
- [ ] Mode switching

### Phase 4: Batman Frontend
- [ ] Dark theme CSS
- [ ] Live video embed
- [ ] Recharts graphs
- [ ] Control panel UI

### Phase 5: Integration
- [ ] Connect all modules in app.py
- [ ] Test auto/manual modes
- [ ] Debug and optimize

## Next Steps
1. Fix ultrasonic GPIO pin conflict
2. Create tracking.py
3. Update app.py with WebSocket
4. Create Batman-themed frontend

Should I continue? This will be ~10+ more files to create/update!
