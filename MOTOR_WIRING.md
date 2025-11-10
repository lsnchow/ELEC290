# L298N Motor Driver Wiring Guide

## 🔌 Complete Wiring Diagram

```
RASPBERRY PI 5                    L298N MOTOR DRIVER
(BCM Pin Numbers)                 
                                  
GPIO 17 (Pin 11) ────────────────> IN1  ─┐
GPIO 27 (Pin 13) ────────────────> IN2  ─┼─> Motor A (OUT1, OUT2)
GPIO 22 (Pin 15) ────────────────> ENA  ─┘    [Left Motor]
                                  
GPIO 23 (Pin 16) ────────────────> IN3  ─┐
GPIO 24 (Pin 18) ────────────────> IN4  ─┼─> Motor B (OUT3, OUT4)
GPIO 25 (Pin 22) ────────────────> ENB  ─┘    [Right Motor]
                                  
GND (Pin 6,9,14,20) ─────────────> GND
                                  
                                  +5V  <────── 5V from Pi OR external
                                  VCC  <────── 6-12V Motor Power Supply
                                  GND  <────── Power Supply Ground
```

## 📍 L298N Terminal Layout

```
┌─────────────────────────────────────┐
│          L298N MOTOR DRIVER         │
├─────────────────────────────────────┤
│                                     │
│  [12V]  [GND]  [5V]     Power In    │
│   VCC    GND   +5V                  │
│                                     │
│  OUT1 OUT2   OUT3 OUT4   Motor Out  │
│  [M1+][M1-]  [M2+][M2-]             │
│    │    │      │    │               │
│    └────┴──────┴────┘               │
│   Motor A    Motor B                │
│   (Left)     (Right)                │
│                                     │
│  [ENA] [IN1][IN2] [IN3][IN4] [ENB]  │
│   PWM   Dir  Dir   Dir  Dir  PWM    │
│    │     │    │     │    │    │     │
│    └─────┴────┴─────┴────┴────┘     │
│         From Raspberry Pi           │
│                                     │
│  Jumpers: [==] ENA    ENB [==]      │
│           (IN PLACE!)               │
└─────────────────────────────────────┘
```

## ✅ Checklist Before Testing

### Power Supply
- [ ] Motor power (6-12V) connected to VCC terminal
- [ ] Power supply GND connected to L298N GND
- [ ] Raspberry Pi GND connected to L298N GND
- [ ] 5V logic power on +5V pin (from Pi or external)

### GPIO Connections (BCM numbering!)
- [ ] GPIO 17 → IN1
- [ ] GPIO 27 → IN2
- [ ] GPIO 22 → ENA
- [ ] GPIO 23 → IN3
- [ ] GPIO 24 → IN4
- [ ] GPIO 25 → ENB

### L298N Configuration
- [ ] ENA jumper is IN PLACE
- [ ] ENB jumper is IN PLACE
- [ ] Left motor connected to OUT1 and OUT2
- [ ] Right motor connected to OUT3 and OUT4

### Software
- [ ] Latest code pulled from GitHub
- [ ] gpiozero installed: `sudo apt install python3-gpiozero python3-lgpio`
- [ ] All Python dependencies installed

## 🔍 Troubleshooting Voltage Issues

### Symptom: Motor driver gets voltage but motors don't turn

**Check with multimeter:**

1. **Power rails:**
   - VCC terminal: Should be 6-12V
   - +5V terminal: Should be ~5V
   - GND: Common ground between Pi and L298N

2. **GPIO signal pins (when commanding motor):**
   - IN1, IN2, IN3, IN4: Should toggle between 0V and 3.3V
   - ENA, ENB: Should show varying voltage (PWM) when motor commanded

3. **Motor output terminals:**
   - OUT1-OUT2: Should show voltage when Motor A commanded
   - OUT3-OUT4: Should show voltage when Motor B commanded

### Possible Issues:

**Issue 1: Jumpers removed**
- **Symptom:** Motors run at full speed regardless of commands
- **Fix:** Put ENA and ENB jumpers back in place

**Issue 2: Wrong GPIO pin numbers**
- **Symptom:** No output voltage on motor terminals
- **Fix:** Verify you're using BCM numbering, not physical pin numbers

**Issue 3: Insufficient motor power**
- **Symptom:** L298N gets warm, motors don't turn
- **Fix:** Ensure VCC has 6-12V, not just 5V

**Issue 4: Code using RPi.GPIO instead of gpiozero**
- **Symptom:** Crash on startup with GPIO error
- **Fix:** Already fixed in latest code - just pull from GitHub

## 🧪 Testing Procedure

### Step 1: Visual inspection
```bash
# Check if all wires are connected
# Verify jumpers are in place
# Confirm power supply is on
```

### Step 2: Run GPIO test
```bash
cd ~/ELEC290_src_test/ELEC290
python3 test_gpio_pins.py
```

This will test each pin individually and show:
- ✓ Which pins are working
- ✗ Which pins are failing
- Full motor sequences (forward/backward)

### Step 3: Run motor test script
```bash
python3 motors.py
```

This runs a predefined sequence:
1. Forward 2 seconds
2. Left 1 second
3. Right 1 second
4. Backward 2 seconds
5. Stop

### Step 4: Run full application
```bash
python3 app.py
```

Then test WASD controls in the web interface.

## 📊 Expected Voltages

**When Motor A Forward (50% speed):**
- IN1 = 3.3V (HIGH)
- IN2 = 0V (LOW)
- ENA = ~1.65V average (50% PWM)
- OUT1-OUT2 = Voltage proportional to motor power

**When Motor A Backward (50% speed):**
- IN1 = 0V (LOW)
- IN2 = 3.3V (HIGH)
- ENA = ~1.65V average (50% PWM)
- OUT1-OUT2 = Voltage proportional to motor power (reversed)

**When Stopped:**
- IN1 = 0V or 3.3V (both HIGH for brake)
- IN2 = 0V or 3.3V (both HIGH for brake)
- ENA = 0V
- OUT1-OUT2 = 0V

## 🆘 Still Not Working?

If motors still don't work after checking everything:

1. **Swap motors** - Test if a specific motor is broken
2. **Try different GPIO pins** - Rule out Pi GPIO damage
3. **Test L298N with Arduino** - Verify L298N isn't damaged
4. **Check motor voltage rating** - Ensure motors match power supply
5. **Measure motor resistance** - Should be low (few ohms), not infinite

## 📞 Quick Debug Commands

```bash
# Pull latest code
cd ~/ELEC290_src_test/ELEC290 && git pull

# Test GPIO pins
python3 test_gpio_pins.py

# Test motors directly
python3 motors.py

# Run full app
python3 app.py

# Check GPIO state (install if needed: sudo apt install gpiod)
gpioinfo | grep -E "17|22|23|24|25|27"
```

Good luck! 🚀
