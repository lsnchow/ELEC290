# 🔧 Arduino Not Reading Data - Troubleshooting Guide

## Problem
Arduino is powered (lights on) but Python code isn't receiving sensor data.

## Quick Diagnosis

### Run the debugger script on your Raspberry Pi:
```bash
python3 debug_arduino.py
```

This will:
1. ✅ List all available serial ports
2. ✅ Test reading from each port
3. ✅ Show raw data being received
4. ✅ Check if JSON parsing works
5. ✅ Verify your permissions

---

## Common Issues & Solutions

### Issue 1: Wrong Serial Port ❌

**Symptom:** `Could not connect to Arduino` message

**Check which port Arduino is on:**
```bash
# Before plugging Arduino
ls /dev/tty*

# Plug in Arduino, then check again
ls /dev/tty*

# The new port is your Arduino!
# Usually /dev/ttyUSB0 or /dev/ttyACM0
```

**Fix:** Update `config.py`:
```python
ARDUINO_PORT = '/dev/ttyACM0'  # Change if needed
```

---

### Issue 2: Arduino IDE Serial Monitor Open ❌

**Symptom:** `Port already in use` error

**Problem:** Only ONE program can use serial port at a time!

**Fix:** 
1. Close Arduino IDE completely
2. If Serial Monitor was open, restart the Python app
3. Make sure nothing else is using the port:
```bash
sudo fuser /dev/ttyUSB0  # Shows what's using the port
```

---

### Issue 3: Arduino Sketch Not Uploaded ❌

**Symptom:** Port opens but no data received

**Check:**
1. Open Arduino IDE
2. Tools → Port → Select your Arduino port
3. Tools → Serial Monitor (set to 9600 baud)
4. You should see JSON lines like: `{"gas":450,"temp":25.5,"dist":10.2}`

**If you see nothing:**
- Sketch not uploaded properly
- Re-upload `arduino_sensors.ino`
- Or upload `arduino_test_simple.ino` to rule out sensor issues

---

### Issue 4: Wrong Baud Rate ❌

**Symptom:** Garbage characters or no data

**Check both match:**
- **Arduino sketch:** `Serial.begin(9600);`
- **config.py:** `ARDUINO_BAUD = 9600`

Common mistake: Arduino set to 115200, Python expecting 9600

---

### Issue 5: Insufficient Permissions ❌

**Symptom:** `Permission denied` when opening port

**Check your groups:**
```bash
groups
```

**Should see:** `dialout` or `uucp` in the list

**Fix:**
```bash
sudo usermod -a -G dialout $USER
# Log out and back in (or reboot)
```

---

### Issue 6: Bad USB Cable ❌

**Symptom:** Arduino powers on but no communication

**Problem:** Some USB cables are power-only (no data lines)

**Test:** Try a different USB cable (use one that came with Arduino or that you know works for data)

---

### Issue 7: DHT Sensor Not Connected ❌

**Symptom:** `dht.readTemperature()` returns NaN, sketch may hang

**Quick test:** Upload `arduino_test_simple.ino` which doesn't use sensors

**Fix in main sketch:**
```cpp
float temperature = dht.readTemperature();
if (isnan(temperature)) {
    temperature = 25.0;  // Default - already in your code!
}
```

---

### Issue 8: Python Serial Module Issues ❌

**Symptom:** Import errors or weird behavior

**Fix:**
```bash
pip3 install --upgrade pyserial
```

---

## Step-by-Step Debug Process

### 1️⃣ Test Arduino Independently

**Upload the simple test sketch:**
```bash
# Upload arduino_test_simple.ino via Arduino IDE
```

**Open Serial Monitor:**
- Tools → Serial Monitor
- Set to 9600 baud
- Should see: `{"gas":XXX,"temp":YY,"dist":ZZ}`

If this works → Arduino + sketch are fine, problem is Python side  
If this doesn't work → Arduino or sketch problem

---

### 2️⃣ Test Python Serial

**Run the debugger:**
```bash
python3 debug_arduino.py
```

Should show:
```
✓ Found 1 serial port(s):
1. /dev/ttyUSB0

✓ Successfully opened /dev/ttyUSB0
[1] RAW: '{"gas":450,"temp":25.5,"dist":10.2}'
     ✓ Valid JSON: {'gas': 450, 'temp': 25.5, 'dist': 10.2}
```

If you see this → Python can read Arduino fine!

---

### 3️⃣ Test Arduino Serial Class

**Run the test directly:**
```bash
python3 arduino_serial.py
```

Should output:
```
✓ Arduino connected on /dev/ttyUSB0
Arduino: Started reading sensor data
Gas: 450, Temp: 25.5°C, Distance: 10.2cm
Gas: 455, Temp: 25.3°C, Distance: 10.5cm
...
```

If this works → `ArduinoSerial` class is fine!

---

### 4️⃣ Check App Integration

**Look for this in app.py output:**
```bash
python3 app.py
```

Should see:
```
✓ Arduino connected on /dev/ttyUSB0
Arduino: Started reading sensor data
```

If you see `⚠️ Could not connect` → Port issue  
If you see `Running in simulation mode` → No Arduino detected

---

## Quick Fixes

### Fix 1: Force a specific port
```python
# In app.py, change initialize_system():
arduino = ArduinoSerial(port='/dev/ttyACM0')  # Try ACM0 instead of USB0
```

### Fix 2: Add more detailed logging
```python
# In arduino_serial.py, add prints in _read_loop():
def _read_loop(self):
    while self.running:
        try:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode('utf-8').strip()
                print(f"DEBUG: Raw line: {line}")  # ADD THIS
                # ... rest of code
```

### Fix 3: Reset Arduino programmatically
```python
# In arduino_serial.py __init__:
self.serial.setDTR(False)
time.sleep(0.1)
self.serial.setDTR(True)
time.sleep(2)
```

### Fix 4: Try different timeout
```python
# In arduino_serial.py __init__:
self.serial = serial.Serial(port, baudrate, timeout=5)  # Longer timeout
```

---

## Common Error Messages

### `Serial exception: [Errno 2] No such file or directory: '/dev/ttyUSB0'`
→ Wrong port or Arduino not plugged in  
→ Run `ls /dev/tty*` to find correct port

### `Serial exception: [Errno 13] Permission denied: '/dev/ttyUSB0'`
→ Need permissions: `sudo usermod -a -G dialout $USER`

### `Serial exception: [Errno 16] Device or resource busy`
→ Port already in use (close Arduino IDE)

### `No data received!`
→ Sketch not uploaded or wrong baud rate

---

## If Nothing Works

### Nuclear option - Full reset:

```bash
# 1. Unplug Arduino
# 2. Close all programs (Arduino IDE, Python app, etc.)
# 3. Reboot Raspberry Pi
sudo reboot

# 4. Plug in Arduino
# 5. Check port
ls /dev/tty* | grep -E 'USB|ACM'

# 6. Test with Arduino IDE Serial Monitor first
# 7. Then try Python app
```

---

## Still Stuck?

### Collect this info:

```bash
# 1. Available ports
ls -la /dev/tty* | grep -E 'USB|ACM'

# 2. Your groups
groups

# 3. Python serial version
python3 -c "import serial; print(serial.VERSION)"

# 4. Arduino IDE can read?
# Open Serial Monitor, set 9600 baud, screenshot output

# 5. Debug script output
python3 debug_arduino.py > debug_output.txt 2>&1
```

Send this info for help debugging!

---

## Success Checklist

- [ ] Arduino sketch uploaded (verify in Serial Monitor)
- [ ] Correct serial port identified (usually /dev/ttyUSB0 or /dev/ttyACM0)
- [ ] Baud rate matches (9600 in both Arduino and Python)
- [ ] Arduino IDE Serial Monitor is CLOSED
- [ ] User has permissions (in dialout group)
- [ ] USB cable works for data (not just power)
- [ ] debug_arduino.py shows data being received
- [ ] arduino_serial.py test mode shows data
- [ ] Web UI shows sensor values updating

Once all checked ✅ → Should work!
