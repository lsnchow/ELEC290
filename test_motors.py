#!/usr/bin/env python3
"""
Motor Test Script for L298N Motor Driver
Tests each motor and direction individually
"""
import sys
import time

print("🚗 L298N Motor Driver Test\n")
print("="*60)

# Import motor controller
try:
    from motors import MotorController
    import config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure you're running this from the project directory!")
    sys.exit(1)

print("Initializing motors...")
motors = MotorController(
    ena=config.ENA,
    in1=config.IN1,
    in2=config.IN2,
    enb=config.ENB,
    in3=config.IN3,
    in4=config.IN4
)

print("\n" + "="*60)
print("WIRING CHECK")
print("="*60)
print("L298N → Raspberry Pi (BCM numbering)")
print(f"  ENA → GPIO {config.ENA} (Physical Pin 11)")
print(f"  IN1 → GPIO {config.IN1} (Physical Pin 13)")
print(f"  IN2 → GPIO {config.IN2} (Physical Pin 15)")
print(f"  ENB → GPIO {config.ENB} (Physical Pin 12)")
print(f"  IN3 → GPIO {config.IN3} (Physical Pin 16)")
print(f"  IN4 → GPIO {config.IN4} (Physical Pin 18)")
print(f"  GND → GND")
print(f"  +12V → Battery/Power Supply (6-12V)")
print(f"  +5V → Can connect to Pi 5V (optional)")
print("\nMotor connections:")
print(f"  OUT1, OUT2 → Left Motor")
print(f"  OUT3, OUT4 → Right Motor")
print("="*60)

def test_motor(name, func, duration=2):
    """Test a motor direction"""
    print(f"\n🔧 Testing: {name}")
    print(f"   Running for {duration} seconds...")
    func(60)  # 60% speed
    time.sleep(duration)
    motors.stop()
    print(f"   ✓ {name} complete")
    time.sleep(1)

try:
    print("\n" + "="*60)
    print("MOTOR TEST SEQUENCE")
    print("="*60)
    print("Watch your motors! They should move in the described direction.")
    print("Press Ctrl+C at any time to stop.")
    input("\nPress ENTER to start test...")
    
    # Test each direction
    test_motor("FORWARD (both motors forward)", motors.forward, 3)
    test_motor("BACKWARD (both motors backward)", motors.backward, 3)
    test_motor("LEFT TURN (right motor forward)", motors.left, 2)
    test_motor("RIGHT TURN (left motor forward)", motors.right, 2)
    
    print("\n" + "="*60)
    print("✅ MOTOR TEST COMPLETE!")
    print("="*60)
    
    # Ask about results
    print("\nDid the motors work correctly?")
    print("1. Yes - All motors worked as expected")
    print("2. No - Motors didn't move")
    print("3. No - Motors moved in wrong direction")
    print("4. No - Only one motor worked")
    
    choice = input("\nYour answer (1-4): ").strip()
    
    if choice == "1":
        print("\n✅ Great! Your motors are working correctly!")
        print("You can now use WASD keys in the web interface to control the robot.")
    elif choice == "2":
        print("\n⚠️  Motors didn't move. Check:")
        print("1. Power supply connected to L298N (6-12V)")
        print("2. L298N jumpers on ENA and ENB pins")
        print("3. Motor wires connected to OUT1/OUT2 and OUT3/OUT4")
        print("4. Wiring matches the pin configuration above")
        print("5. Run: sudo python3 test_motors.py (may need sudo)")
    elif choice == "3":
        print("\n⚠️  Motors moved in wrong direction. Fix:")
        print("1. For LEFT motor: Swap OUT1 and OUT2 wires")
        print("2. For RIGHT motor: Swap OUT3 and OUT4 wires")
        print("3. Or update IN1/IN2 logic in code")
    elif choice == "4":
        print("\n⚠️  Only one motor worked. Check:")
        print("1. Both motors connected?")
        print("2. Both motor wires firmly connected?")
        print("3. Try swapping the working/non-working motors")
        print("4. Check L298N has both jumpers on ENA and ENB")
    
except KeyboardInterrupt:
    print("\n\n⏹️  Test stopped by user")
except Exception as e:
    print(f"\n❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\nCleaning up...")
    motors.cleanup()
    print("Done!")

print("\n" + "="*60)
print("Next steps:")
print("1. If motors work → Start app.py and test WASD control")
print("2. If motors don't work → Check wiring and power supply")
print("3. For auto-tracking → Switch to 'Auto Track' mode in web UI")
print("="*60)
