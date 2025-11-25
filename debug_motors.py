#!/usr/bin/env python3
"""
Motor Debug Script - Comprehensive L298N Diagnostics
Tests GPIO output, checks pin states, and provides detailed debugging info
"""
import time
import sys

try:
    from gpiozero import OutputDevice, PWMOutputDevice
    print("✓ gpiozero imported successfully")
except ImportError as e:
    print(f"✗ Failed to import gpiozero: {e}")
    print("Install with: sudo apt install python3-gpiozero python3-lgpio")
    sys.exit(1)

# Pin definitions
ENA = 22
IN1 = 17
IN2 = 27
ENB = 25
IN3 = 23
IN4 = 24

print("\n" + "="*70)
print("L298N MOTOR DRIVER DEBUG TOOL")
print("="*70)
print(f"\nPin Configuration (BCM numbering):")
print(f"  Motor A (Left):  IN1={IN1}, IN2={IN2}, ENA={ENA}")
print(f"  Motor B (Right): IN3={IN3}, IN4={IN4}, ENB={ENB}")
print("\n" + "="*70)

def test_pin_output(pin_num, pin_name):
    """Test if a pin can be controlled"""
    print(f"\nTesting {pin_name} (GPIO {pin_num})...")
    try:
        pin = OutputDevice(pin_num, active_high=True, initial_value=False)
        print(f"  ✓ Pin initialized")
        
        pin.on()
        print(f"  ✓ Set HIGH - measure pin with multimeter (should be 3.3V)")
        time.sleep(2)
        
        pin.off()
        print(f"  ✓ Set LOW - measure pin with multimeter (should be 0V)")
        time.sleep(1)
        
        pin.close()
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

def test_pwm_output(pin_num, pin_name):
    """Test if a PWM pin can be controlled"""
    print(f"\nTesting {pin_name} (GPIO {pin_num}) - PWM...")
    try:
        pin = PWMOutputDevice(pin_num, frequency=1000, initial_value=0.0)
        print(f"  ✓ PWM initialized at 1000 Hz")
        
        print(f"  Setting PWM to 0% (OFF)...")
        pin.value = 0.0
        time.sleep(1)
        
        print(f"  Setting PWM to 50% - measure with multimeter (~1.65V average)")
        pin.value = 0.5
        time.sleep(2)
        
        print(f"  Setting PWM to 100% (ON) - measure with multimeter (~3.3V)")
        pin.value = 1.0
        time.sleep(2)
        
        pin.value = 0.0
        pin.close()
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

print("\nPHASE 1: Testing Individual GPIO Pins")
print("="*70)
print("Get your multimeter ready - we'll test each pin individually\n")
input("Press ENTER to start...")

results = {}
results['IN1'] = test_pin_output(IN1, "IN1")
results['IN2'] = test_pin_output(IN2, "IN2")
results['IN3'] = test_pin_output(IN3, "IN3")
results['IN4'] = test_pin_output(IN4, "IN4")
results['ENA'] = test_pwm_output(ENA, "ENA")
results['ENB'] = test_pwm_output(ENB, "ENB")

print("\n" + "="*70)
print("PHASE 1 RESULTS:")
print("="*70)
for pin, passed in results.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{pin:10} {status}")

if not all(results.values()):
    print("\n⚠️  Some GPIO pins failed to initialize!")
    print("Possible issues:")
    print("  - Pins already in use by another process")
    print("  - GPIO permissions issue")
    print("  - Hardware problem with Raspberry Pi")
    sys.exit(1)

print("\n✓ All GPIO pins working correctly!")

print("\n" + "="*70)
print("PHASE 2: Testing Motor A (Left Motor)")
print("="*70)
print("\nNOW checking if motor actually spins...")
print("Watch/listen to the LEFT motor during this test\n")
input("Press ENTER to test Motor A...")

try:
    in1 = OutputDevice(IN1, active_high=True, initial_value=False)
    in2 = OutputDevice(IN2, active_high=True, initial_value=False)
    ena = PWMOutputDevice(ENA, frequency=1000, initial_value=0.0)
    
    print("\n1. Motor A FORWARD at 30% speed for 3 seconds...")
    print(f"   IN1={IN1} → HIGH (3.3V)")
    print(f"   IN2={IN2} → LOW (0V)")
    print(f"   ENA={ENA} → 30% PWM (~1V average)")
    print(f"   Expected: LEFT motor spins SLOWLY forward")
    print(f"   Measure OUT1-OUT2 on L298N: should show voltage!\n")
    in1.on()
    in2.off()
    ena.value = 0.3
    time.sleep(3)
    
    print("\n2. Motor A FORWARD at 70% speed for 3 seconds...")
    print(f"   ENA={ENA} → 70% PWM (~2.3V average)")
    print(f"   Expected: LEFT motor spins FASTER forward\n")
    ena.value = 0.7
    time.sleep(3)
    
    print("\n3. STOPPING Motor A...")
    in1.off()
    in2.off()
    ena.value = 0.0
    time.sleep(1)
    
    print("\n4. Motor A BACKWARD at 50% speed for 3 seconds...")
    print(f"   IN1={IN1} → LOW (0V)")
    print(f"   IN2={IN2} → HIGH (3.3V)")
    print(f"   ENA={ENA} → 50% PWM (~1.65V average)")
    print(f"   Expected: LEFT motor spins backward\n")
    in1.off()
    in2.on()
    ena.value = 0.5
    time.sleep(3)
    
    print("\n5. STOPPING Motor A...")
    in1.off()
    in2.off()
    ena.value = 0.0
    
    in1.close()
    in2.close()
    ena.close()
    
    print("\n" + "="*70)
    motor_a_worked = input("Did Motor A spin? (y/n): ").lower().strip() == 'y'
    
except Exception as e:
    print(f"\n✗ Motor A test FAILED: {e}")
    import traceback
    traceback.print_exc()
    motor_a_worked = False

print("\n" + "="*70)
print("PHASE 3: Testing Motor B (Right Motor)")
print("="*70)
print("\nWatch/listen to the RIGHT motor during this test\n")
input("Press ENTER to test Motor B...")

try:
    in1_b = OutputDevice(IN3, active_high=True, initial_value=False)
    in2_b = OutputDevice(IN4, active_high=True, initial_value=False)
    enb = PWMOutputDevice(ENB, frequency=1000, initial_value=0.0)
    
    print("\n1. Motor B FORWARD at 30% speed for 3 seconds...")
    print(f"   IN3={IN3} → HIGH (3.3V)")
    print(f"   IN4={IN4} → LOW (0V)")
    print(f"   ENB={ENB} → 30% PWM (~1V average)")
    print(f"   Expected: RIGHT motor spins SLOWLY forward")
    print(f"   Measure OUT3-OUT4 on L298N: should show voltage!\n")
    in1_b.on()
    in2_b.off()
    enb.value = 0.3
    time.sleep(3)
    
    print("\n2. Motor B FORWARD at 70% speed for 3 seconds...")
    print(f"   ENB={ENB} → 70% PWM (~2.3V average)")
    print(f"   Expected: RIGHT motor spins FASTER forward\n")
    enb.value = 0.7
    time.sleep(3)
    
    print("\n3. STOPPING Motor B...")
    in1_b.off()
    in2_b.off()
    enb.value = 0.0
    time.sleep(1)
    
    print("\n4. Motor B BACKWARD at 50% speed for 3 seconds...")
    print(f"   IN3={IN3} → LOW (0V)")
    print(f"   IN4={IN4} → HIGH (3.3V)")
    print(f"   ENB={ENB} → 50% PWM (~1.65V average)")
    print(f"   Expected: RIGHT motor spins backward\n")
    in1_b.off()
    in2_b.on()
    enb.value = 0.5
    time.sleep(3)
    
    print("\n5. STOPPING Motor B...")
    in1_b.off()
    in2_b.off()
    enb.value = 0.0
    
    in1_b.close()
    in2_b.close()
    enb.close()
    
    print("\n" + "="*70)
    motor_b_worked = input("Did Motor B spin? (y/n): ").lower().strip() == 'y'
    
except Exception as e:
    print(f"\n✗ Motor B test FAILED: {e}")
    import traceback
    traceback.print_exc()
    motor_b_worked = False

print("\n" + "="*70)
print("FINAL DIAGNOSIS")
print("="*70)

if motor_a_worked and motor_b_worked:
    print("\n✓✓✓ SUCCESS! Both motors work!")
    print("\nYour wiring is correct. The issue must be in your main code.")
    print("Check app.py and motors.py for bugs.\n")
elif motor_a_worked and not motor_b_worked:
    print("\n⚠️  Motor A works, but Motor B doesn't")
    print("\nCheck Motor B wiring:")
    print("  1. Verify OUT3-OUT4 connections to right motor")
    print("  2. Check right motor isn't damaged (swap motors to test)")
    print("  3. Verify IN3, IN4, ENB wiring from Pi to L298N")
    print("  4. Check ENB jumper is IN PLACE on L298N\n")
elif not motor_a_worked and motor_b_worked:
    print("\n⚠️  Motor B works, but Motor A doesn't")
    print("\nCheck Motor A wiring:")
    print("  1. Verify OUT1-OUT2 connections to left motor")
    print("  2. Check left motor isn't damaged (swap motors to test)")
    print("  3. Verify IN1, IN2, ENA wiring from Pi to L298N")
    print("  4. Check ENA jumper is IN PLACE on L298N\n")
else:
    print("\n✗✗✗ NEITHER motor works!")
    print("\nCommon issues:")
    print("\n1. L298N POWER SUPPLY:")
    print("   ✓ Check VCC has 6-12V from external power supply")
    print("   ✓ Check +5V terminal connected to Pi 5V (Pin 2 or 4)")
    print("   ✓ Check GND from PSU connected to L298N GND")
    print("   ✓ Check GND from Pi connected to L298N GND (COMMON GROUND!)")
    
    print("\n2. L298N JUMPERS:")
    print("   ✓ ENA jumper must be IN PLACE")
    print("   ✓ ENB jumper must be IN PLACE")
    print("   (Without jumpers, no power reaches motors!)")
    
    print("\n3. MOTOR CONNECTIONS:")
    print("   ✓ Left motor connected to OUT1 and OUT2")
    print("   ✓ Right motor connected to OUT3 and OUT4")
    print("   ✓ Motors are DC motors (not servos)")
    
    print("\n4. MULTIMETER CHECKS:")
    print("   During forward test, measure on L298N:")
    print("   ✓ VCC terminal: should be 6-12V")
    print("   ✓ +5V terminal: should be ~5V")
    print("   ✓ OUT1-OUT2: should show motor voltage when enabled")
    print("   ✓ IN1: should be 3.3V when HIGH")
    print("   ✓ ENA: should show ~1.65V at 50% PWM")
    
    print("\n5. TEST WITH DIRECT POWER:")
    print("   Connect motor directly to PSU 7V:")
    print("   - Motor spins? → Motor is good, L298N issue")
    print("   - Motor doesn't spin? → Motor is damaged")
    
print("\n" + "="*70)
print("DEBUG COMPLETE")
print("="*70 + "\n")
