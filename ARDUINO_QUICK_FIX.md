# 🚨 Arduino Not Reading? - Quick Fix Guide

## Run This First 👇

```bash
# On your Raspberry Pi, run:
python3 debug_arduino.py
```

This will tell you EXACTLY what's wrong!

---

## Most Common Issues

### 1. Wrong Port? 🔌
```bash
# Find your Arduino:
ls /dev/tty* | grep -E 'USB|ACM'

# Update config.py to match:
ARDUINO_PORT = '/dev/ttyACM0'  # or whatever you found
```

### 2. Arduino IDE Open? 💻
**Close Arduino IDE Serial Monitor!** Only one program can use the port at a time.

### 3. Sketch Not Uploaded? 📤
```bash
# Test Arduino independently:
# 1. Open Arduino IDE
# 2. Tools → Serial Monitor
# 3. Set to 9600 baud
# 4. Should see: {"gas":450,"temp":25.5,"dist":10.2}
```

### 4. Permission Denied? 🔒
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### 5. Enable Debug Mode 🐛
```python
# In config.py:
ARDUINO_DEBUG = True

# Restart app.py - you'll see detailed logs
```

---

## Test Without Sensors

Upload this minimal sketch first:
```bash
# Upload arduino_test_simple.ino via Arduino IDE
# This sends fake data - no sensors needed!
```

---

## Direct Test

```bash
# Test Arduino serial class directly:
python3 arduino_serial.py

# Should show:
# Gas: 450, Temp: 25.5°C, Distance: 10.2cm
```

---

## Still Stuck?

Read the full guide: **ARDUINO_DEBUG.md**

Or collect debug info:
```bash
python3 debug_arduino.py > debug.txt 2>&1
# Send debug.txt for help
```
