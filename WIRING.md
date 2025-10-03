# HC-SR04 Ultrasonic Sensor Wiring Guide

## ⚠️ CRITICAL: Voltage Divider Required!

The HC-SR04 ECHO pin outputs **5V**, but Raspberry Pi GPIO pins are only **3.3V tolerant**. 
**YOU MUST USE A VOLTAGE DIVIDER** or you risk damaging your Raspberry Pi!

---

## Components Needed

- HC-SR04 Ultrasonic Sensor
- 1x 1kΩ Resistor (1000 ohm)
- 1x 2kΩ Resistor (2000 ohm)
- Breadboard
- 4x Jumper wires

---

## Wiring Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    HC-SR04 Sensor                       │
│  ┌───────┐                                              │
│  │ VCC   │──────────────────────────────────────────┐  │
│  │ TRIG  │────────────────────────┐                 │  │
│  │ ECHO  │─────────┐              │                 │  │
│  │ GND   │────┐    │              │                 │  │
│  └───────┘    │    │              │                 │  │
└───────────────│────│──────────────│─────────────────│──┘
                │    │              │                 │
                │    │              │                 │
                │    │   ┌──────────┴──────────┐      │
                │    │   │    1kΩ Resistor     │      │
                │    │   └──────────┬──────────┘      │
                │    │              │                 │
                │    │              ├─────────────────┼──→ GPIO 24 (Pin 18)
                │    │              │                 │
                │    │   ┌──────────┴──────────┐      │
                │    │   │    2kΩ Resistor     │      │
                │    │   └──────────┬──────────┘      │
                │    │              │                 │
                │    └──────────────┼─────────────────┼──→ GPIO 23 (Pin 16)
                │                   │                 │
                └───────────────────┴─────────────────┴──→ GND (Pin 6)
                                                       └──→ 5V (Pin 2)

```

---

## Step-by-Step Instructions

### 1. **Prepare Your Breadboard**
   - Insert the HC-SR04 sensor into the breadboard
   - The four pins should be in separate rows

### 2. **Connect VCC (Power)**
   ```
   HC-SR04 VCC → Raspberry Pi Pin 2 (5V)
   ```
   - Use a red jumper wire

### 3. **Connect GND (Ground)**
   ```
   HC-SR04 GND → Raspberry Pi Pin 6 (GND)
   ```
   - Use a black jumper wire

### 4. **Connect TRIG (Trigger)**
   ```
   HC-SR04 TRIG → Raspberry Pi Pin 16 (GPIO 23)
   ```
   - Use any colored jumper wire (e.g., yellow)
   - This connection is **direct** (no resistors needed)

### 5. **Connect ECHO with Voltage Divider** ⚠️ **MOST IMPORTANT**
   
   a. Connect HC-SR04 ECHO pin to one end of the **1kΩ resistor**
   
   b. Connect the other end of the 1kΩ resistor to:
      - Raspberry Pi **Pin 18 (GPIO 24)**
      - AND one end of the **2kΩ resistor**
   
   c. Connect the other end of the 2kΩ resistor to:
      - Raspberry Pi **Pin 6 (GND)** (same ground as step 3)

---

## Voltage Divider Calculation

The voltage divider formula:
```
V_out = V_in × (R2 / (R1 + R2))
V_out = 5V × (2kΩ / (1kΩ + 2kΩ))
V_out = 5V × (2/3)
V_out = 3.33V ✓ Safe for Raspberry Pi!
```

---

## Physical Pin Layout Reference

```
Raspberry Pi 5 GPIO Header (Top View)

    3.3V  [ 1] [ 2]  5V ◄────────── HC-SR04 VCC (Red)
         [ 3] [ 4]  5V
         [ 5] [ 6]  GND ◄───────── HC-SR04 GND (Black) + 2kΩ resistor
         [ 7] [ 8]
     GND [ 9] [10]
         [11] [12]
         [13] [14]  GND
         [15] [16]  GPIO 23 ◄───── HC-SR04 TRIG (Yellow)
    3.3V [17] [18]  GPIO 24 ◄───── HC-SR04 ECHO via 1kΩ→2kΩ divider (Green)
         [19] [20]  GND
         ...
```

---

## Testing Your Wiring

Before running the main application, test the sensor:

```bash
cd ELEC290-src
source venv/bin/activate
python ultrasonic.py
```

You should see distance readings updating in real-time. If you see errors:

1. **Check all connections** - ensure wires are firmly inserted
2. **Verify resistor values** - use a multimeter if available
3. **Test GPIO pins** - run `gpio readall` (requires wiringpi)
4. **Check sensor orientation** - the metal cylinders should face outward

---

## Common Mistakes to Avoid

❌ **DO NOT** connect ECHO directly to GPIO 24 without resistors
❌ **DO NOT** use different resistor values (the ratio must be 1:2)
❌ **DO NOT** connect VCC to 3.3V (sensor needs 5V to operate)
❌ **DO NOT** swap the TRIG and ECHO pins

✅ **DO** double-check all connections before powering on
✅ **DO** use a breadboard for easier troubleshooting
✅ **DO** keep wires neat and organized

---

## Breadboard Layout Example

```
Breadboard Rows:
─────────────────────────────────────
    a  b  c  d  e     f  g  h  i  j
─────────────────────────────────────
1   [VCC] → → → →  [RED WIRE to Pi Pin 2]
2   [TRIG]→ → → →  [YELLOW WIRE to Pi Pin 16]
3   [ECHO]→ → → →  [1kΩ]→ → → 
4         → → → →  [Junction: to GPIO24 + 2kΩ]
5   [GND] → → → →  [2kΩ to GND]
6         → → → →  [BLACK WIRE to Pi Pin 6]
```

---

## Visual Reference for Resistors

**1kΩ Resistor Color Bands:**
- Brown, Black, Red, Gold
- Or: Brown, Black, Black, Brown, Brown

**2kΩ Resistor Color Bands:**
- Red, Black, Red, Gold
- Or: Red, Black, Black, Brown, Brown

If unsure, use a multimeter to verify resistance values.

---

## Need Help?

If the sensor still doesn't work:
1. Check the README.md troubleshooting section
2. Verify Python dependencies are installed
3. Make sure you're running the code on the Pi (not your Mac)
4. Test with a known-working HC-SR04 sensor

---

**Remember: The voltage divider is NOT optional! Protect your Pi!** 🛡️
