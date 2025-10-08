# Arduino Showing Zero Values - Quick Fix Guide

## Problem: Arduino was working, unplugged it, now showing zeros

This is a common issue after unplugging/replugging the Arduino while app.py is running.

---

## 🚀 QUICK FIX (Most Common)

### Solution 1: Restart app.py
The serial connection is lost when you unplug. Simply restart:

**On Raspberry Pi:**
```bash
# Stop the running app (Ctrl+C if running in terminal)
# Or if running in background:
pkill -f app.py

# Restart
python3 app.py
```

The app has auto-port detection and will reconnect automatically!

---

### Solution 2: Arduino IDE Serial Monitor Is Open
If Arduino IDE's Serial Monitor is open, it **locks the port** and Python can't read it.

**Fix:**
1. Open Arduino IDE
2. Close the Serial Monitor (top-right X button)
3. Restart app.py

---

### Solution 3: Wait for Arduino to Reset
When you plug in Arduino, it takes 2-3 seconds to reset and start sending data.

**Fix:**
```bash
# Wait 3 seconds after plugging in, then:
python3 app.py
```

---

## 🔍 DIAGNOSTIC TOOLS

### Tool 1: Check if Arduino is sending data
```bash
python3 fix_arduino_connection.py
```

This will:
- List all serial ports
- Test each port for Arduino data
- Show you raw JSON output
- Tell you which port Arduino is on

### Tool 2: Manual check with screen/minicom
```bash
# Install screen if needed
sudo apt-get install screen

# Connect to Arduino (try both ports)
screen /dev/ttyUSB0 9600
# or
screen /dev/ttyACM0 9600

# You should see:
# {"accelX":-0.31,"accelY":0.05,"accelZ":10.58,...}

# To exit: Ctrl+A, then K, then Y
```

### Tool 3: Check Arduino is detected
```bash
# List USB devices
ls /dev/tty* | grep -E 'USB|ACM'

# You should see something like:
# /dev/ttyUSB0
# or
# /dev/ttyACM0
```

---

## 🐛 DEEPER ISSUES

### Issue 1: No /dev/ttyUSB* or /dev/ttyACM* found

**Symptoms:** `ls /dev/tty*` shows no USB/ACM ports

**Solutions:**
1. Check USB cable is data cable (not charge-only)
2. Try different USB port on Raspberry Pi
3. Check Arduino has power (LED should be on)
4. Try: `lsusb` to see if USB device is detected at all

### Issue 2: Permission Denied

**Symptoms:** Error like "Permission denied: '/dev/ttyUSB0'"

**Solution:**
```bash
# Add your user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in, or:
sudo reboot
```

### Issue 3: Wrong Sketch Uploaded

**Symptoms:** Arduino connected but no JSON data, or wrong format

**Solution:**
1. Open `arduino_sensors.ino` in Arduino IDE
2. Select your board (Tools → Board → Arduino Uno)
3. Select port (Tools → Port → /dev/ttyUSB0 or /dev/ttyACM0)
4. Click Upload (→ button)
5. Wait for "Done uploading"
6. **Close Serial Monitor**
7. Restart app.py

### Issue 4: App.py shows old/cached data

**Symptoms:** Values don't change, stuck at same numbers

**Solution:**
```bash
# Hard restart
pkill -f app.py
sleep 2
python3 app.py
```

---

## 📊 VERIFY IT'S WORKING

### In Terminal (when app.py starts):
```
✓ Arduino connected on /dev/ttyUSB0
[Arduino] Raw: '{"accelX":-0.31,"accelY":0.05,...}'
[Arduino] Parsed: accel=(-0.31,0.05,10.58), ...
```

### In Web UI:
- Arduino Status: **CONNECTED** (top-right)
- MPU6050 values should be updating
- Accel Z should be around **9.8** (gravity)
- Temperature around **20-30°C**
- Chart should be drawing

---

## 🆘 NUCLEAR OPTION

If nothing works, do a complete reset:

```bash
# 1. Stop everything
pkill -f app.py

# 2. Unplug Arduino USB

# 3. Close Arduino IDE completely

# 4. Wait 5 seconds

# 5. Plug Arduino back in

# 6. Wait 3 seconds for Arduino to reset

# 7. Git pull latest code
cd ~/robot
git pull

# 8. Restart app
python3 app.py

# 9. Check web UI after 5 seconds
```

---

## 💡 PREVENTION

To avoid this issue in the future:

1. **Don't unplug Arduino while app.py is running**
   - Stop app.py first (Ctrl+C)
   - Then unplug Arduino
   
2. **Always close Arduino IDE Serial Monitor**
   - Serial Monitor locks the port
   - Python can't read if it's open

3. **Use systemd service** (restart automatically)
   - See DEPLOYMENT.md for setup
   - Auto-restarts if connection lost

---

## 🔧 DEBUG CHECKLIST

Run through this checklist:

- [ ] Arduino has power (LED is on)
- [ ] USB cable is connected
- [ ] Arduino IDE Serial Monitor is **closed**
- [ ] Ran `python3 fix_arduino_connection.py` successfully
- [ ] Restarted app.py
- [ ] Waited 5+ seconds after restart
- [ ] Refreshed web browser
- [ ] Checked browser console for errors (F12)

If all checked and still not working → check hardware connections (MPU6050 wiring).

---

## 📞 STILL NOT WORKING?

1. Run diagnostic: `python3 fix_arduino_connection.py`
2. Check browser console (F12 → Console tab)
3. Check terminal output from app.py
4. Share the output for help
