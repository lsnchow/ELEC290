# UI Update & Motor Debugging Guide

## ✅ Completed Changes

### 1. UI Redesign - Air Quality Monitoring Robot
- **Title Changed**: "ELEC290 Air Quality Monitoring Robot"
- **New Layout**: 
  - Camera feed on LEFT
  - All sensors on RIGHT (organized panels)
  - WASD controls at BOTTOM (compact horizontal bar)

### 2. Air Quality Sensor Display
Added real-time air quality monitoring with color-coded status:

**CO₂ (Carbon Dioxide)**
- Good: < 800 ppm (green)
- Moderate: 800-1200 ppm (yellow)
- Poor: > 1200 ppm (red)

**TVOC (Total Volatile Organic Compounds)**
- Good: < 220 ppb (green)
- Moderate: 220-660 ppb (yellow)
- Poor: > 660 ppb (red)

**MQ-2 Gas Sensor**
- Normal: < 300 (green)
- Elevated: 300-500 (yellow)
- High: > 500 (red)

### 3. Motor Controller Bug Fix
Fixed missing pin variable storage in `motors.py`:
- Added `self.in1`, `self.in2`, `self.in3`, `self.in4`, `self.ena`, `self.enb`
- This fixes motor control for both gpiozero and RPi.GPIO modes

---

## 🔧 Motor Not Working - Debugging Steps

### On Raspberry Pi:

1. **Pull latest code:**
   ```bash
   cd ~/ELEC290_src_test/ELEC290
   git pull
   ```

2. **Run GPIO test script:**
   ```bash
   python3 test_gpio_pins.py
   ```
   
   This will:
   - Test each GPIO pin individually
   - Test full motor sequences (forward/backward)
   - Show which pins/motors are working
   - Provide troubleshooting guidance

3. **What to check if motors don't work:**
   
   **Power Issues:**
   - L298N needs **separate motor power** (6-12V on VCC terminal)
   - 5V logic power on +5V pin (from Pi or external)
   - Check ground is connected between Pi and L298N
   
   **Wiring Check (BCM pin numbers):**
   ```
   Motor A (Left):
   - IN1 = GPIO 17 (Physical Pin 11)
   - IN2 = GPIO 27 (Physical Pin 13)
   - ENA = GPIO 22 (Physical Pin 15)
   
   Motor B (Right):
   - IN3 = GPIO 23 (Physical Pin 16)
   - IN4 = GPIO 24 (Physical Pin 18)
   - ENB = GPIO 25 (Physical Pin 22)
   ```
   
   **L298N Jumpers:**
   - Ensure ENA and ENB jumpers are IN PLACE (for PWM speed control)
   - If removed, motors run at full speed always
   
   **Motor Connections:**
   - Motor A (Left) → OUT1 and OUT2 on L298N
   - Motor B (Right) → OUT3 and OUT4 on L298N

4. **Test with manual script:**
   ```bash
   python3 motors.py
   ```
   This runs a test sequence (forward, left, right, backward).

---

## 🚀 Running the Application

### On Raspberry Pi:

```bash
cd ~/ELEC290_src_test/ELEC290
git pull
python3 app.py
```

### On Your Mac (with SSH tunnel):

```bash
ssh -L 5000:localhost:5000 raspberry@<PI_IP_ADDRESS>
```

Then open: **http://localhost:5000**

---

## 📊 New UI Features

### Right Panel Sensors (Top to Bottom):
1. **Air Quality Monitoring** - CO₂, TVOC, MQ-2, Temperature
2. **MPU6050 Accelerometer** - X, Y, Z axes
3. **MPU6050 Gyroscope** - X, Y, Z axes  
4. **Distance Sensor** - Ultrasonic (HC-SR04)
5. **System Status** - Arduino, Tracking, Motors, Last Update
6. **Data Logging** - Download CSV, view statistics

### Bottom Control Bar:
- **Mode buttons**: Manual / Auto Track
- **WASD controls**: W, A, S, D (compact)
- **Emergency Stop**: Red button

---

## 🐛 Common Issues & Solutions

### Issue: Motors not responding
**Solution:** Run `python3 test_gpio_pins.py` to identify which pins fail

### Issue: Air quality shows "--"
**Solution:** 
- Check Arduino is connected (green "CONNECTED" in System Status)
- Verify CCS811 sensor is properly wired (I2C: SDA/SCL)
- Check MQ-2 sensor on A0

### Issue: "Cannot determine SOC peripheral base address"
**Solution:** This is the old RPi.GPIO error - should be fixed now with gpiozero

### Issue: Motors receive voltage but don't spin
**Possible causes:**
1. ENA/ENB jumpers removed (motors need PWM)
2. Wrong GPIO pins (use BCM numbering, not physical)
3. Motor power supply too low (needs 6-12V)
4. Faulty L298N board

---

## 📁 Files Modified

1. **templates/index.html** - Complete UI redesign
2. **motors.py** - Fixed pin variable storage bug
3. **test_gpio_pins.py** - NEW: GPIO debugging tool

---

## 🎯 Next Steps

1. **Run GPIO test** on Raspberry Pi to identify motor issue
2. **Fix wiring** based on test results
3. **Test air quality sensors** - verify CCS811 and MQ-2 readings
4. **Upload Arduino sketch** if you haven't already (`arduino_sensors.ino`)

---

## 📸 Expected UI Layout

```
┌─────────────────────────────────────────────────────────┐
│  ELEC290 AIR QUALITY MONITORING ROBOT                   │
└─────────────────────────────────────────────────────────┘
┌──────────────────────┬──────────────────────────────────┐
│                      │  AIR QUALITY MONITORING          │
│   CAMERA FEED        │  CO₂ | TVOC | MQ-2 | Temp       │
│   (Left Side)        ├──────────────────────────────────┤
│                      │  MPU6050 ACCELEROMETER           │
│   640x480            │  X | Y | Z                       │
│                      ├──────────────────────────────────┤
│   FPS: 15            │  MPU6050 GYROSCOPE               │
│   Detections: 1      │  X | Y | Z                       │
│   Mode: MANUAL       ├──────────────────────────────────┤
│                      │  DISTANCE SENSOR                 │
│                      │  Ultrasonic: 45.2 cm             │
│                      ├──────────────────────────────────┤
│                      │  SYSTEM STATUS                   │
│                      │  Arduino: CONNECTED              │
│                      │  Tracking: DISABLED              │
│                      │  Motor Dir: STOPPED              │
│                      │  Motor Speed: 0%                 │
│                      ├──────────────────────────────────┤
│                      │  DATA LOGGING                    │
│                      │  📥 Download CSV | Clear         │
└──────────────────────┴──────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  Mode: [Manual] [Auto]  |  Movement: [W][A][S][D]  | ⚠️ STOP │
└─────────────────────────────────────────────────────────┘
```

Good luck debugging! 🎉
