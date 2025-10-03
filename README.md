# Raspberry Pi Human Detection & Distance Monitoring System

A real-time human detection system using YOLOv8 with ultrasonic distance monitoring, streaming via MJPEG to a web interface.

## Features
- 🎥 Real-time webcam feed with YOLOv8 human detection
- 📏 HC-SR04 ultrasonic distance measurement
- 🌐 MJPEG streaming to web interface
- 🎯 Bounding boxes and detection counts
- 📊 Live distance readings overlaid on video

## Hardware Requirements
- Raspberry Pi 5
- USB Webcam (or Pi Camera)
- HC-SR04 Ultrasonic Sensor
- Resistors: 1kΩ and 2kΩ (for voltage divider)
- Breadboard and jumper wires

## HC-SR04 Wiring with Voltage Divider

⚠️ **IMPORTANT**: The HC-SR04 ECHO pin outputs 5V, but Raspberry Pi GPIO pins are only 3.3V tolerant. You MUST use a voltage divider to prevent damage!

### Wiring Diagram:
```
HC-SR04          Raspberry Pi 5
--------         --------------
VCC     ──────→  Pin 2 (5V)
TRIG    ──────→  Pin 16 (GPIO 23)
                 
ECHO    ──┬───→  [1kΩ Resistor] ──┬──→ Pin 18 (GPIO 24)
          │                       │
          └───→  [2kΩ Resistor] ──┴──→ Pin 6 (GND)
          
GND     ──────→  Pin 6 (GND)
```

### Voltage Divider Explanation:
- The ECHO pin connects to a 1kΩ resistor
- The other end of the 1kΩ resistor connects to GPIO 24 AND a 2kΩ resistor
- The 2kΩ resistor connects to Ground
- This creates a 5V × (2kΩ/(1kΩ+2kΩ)) = 3.33V output, safe for the Pi

### Physical Pin Layout:
```
    3.3V [ 1] [ 2] 5V ──────────── VCC (HC-SR04)
         [ 3] [ 4] 5V
         [ 5] [ 6] GND ──────────── GND (HC-SR04) + 2kΩ resistor
         ...
         [15] [16] GPIO 23 ──────── TRIG (HC-SR04)
         [17] [18] GPIO 24 ──────── ECHO (via voltage divider)
```

## Installation on Raspberry Pi

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ELEC290-src
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Wire the HC-SR04 sensor** (see wiring diagram above)

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the web interface:**
   - On your Mac, open a browser and navigate to:
   - `http://<raspberry-pi-ip>:5000`
   - To find your Pi's IP: `hostname -I` on the Pi

## Usage

- The webapp will display the live camera feed
- Detected humans will be highlighted with bounding boxes
- Detection count shows in the top-left corner
- Distance from ultrasonic sensor displays in the top-right corner
- Press `Ctrl+C` in the terminal to stop the server

## Configuration

Edit `config.py` to change:
- Camera resolution
- Detection confidence threshold
- GPIO pins
- Server host/port

## Troubleshooting

**No video feed:**
- Check if camera is connected: `ls /dev/video*`
- Try different camera index in `config.py`

**Ultrasonic sensor not working:**
- Verify wiring and voltage divider
- Test GPIO pins: `gpio readall`
- Check permissions: add user to gpio group

**Slow performance:**
- Lower resolution in `config.py`
- Use YOLOv8n (nano) model for speed
- Close other applications on Pi

## Project Structure
```
ELEC290-src/
├── app.py              # Main Flask application
├── detector.py         # YOLOv8 detection module
├── ultrasonic.py       # HC-SR04 sensor module
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Web interface
└── README.md          # This file
```

## License
MIT
