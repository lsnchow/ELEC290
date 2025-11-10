#!/usr/bin/env python3
"""
GPIO Pin Tester for L298N Motor Driver
Tests each pin individually to verify wiring

Run this on the Raspberry Pi to test motor connections
"""
import time
from gpiozero import OutputDevice, PWMOutputDevice

# Pin definitions (BCM numbering)
ENA = 22  # Motor A PWM
IN1 = 17  # Motor A Direction 1
IN2 = 27  # Motor A Direction 2
ENB = 25  # Motor B PWM
IN3 = 23  # Motor B Direction 1
IN4 = 24  # Motor B Direction 2

def test_pin(pin_num, pin_name, is_pwm=False):
    """Test a single GPIO pin"""
    print(f"\n{'='*50}")
    print(f"Testing {pin_name} (BCM {pin_num})")
    print(f"{'='*50}")
    
    try:
        if is_pwm:
            # Test PWM pin
            print(f"Creating PWM output on pin {pin_num}...")
            pin = PWMOutputDevice(pin_num, frequency=1000, initial_value=0.0)
            
            print("Setting PWM to 50%...")
            pin.value = 0.5
            time.sleep(2)
            
            print("Setting PWM to 100%...")
            pin.value = 1.0
            time.sleep(2)
            
            print("Setting PWM to 0%...")
            pin.value = 0.0
            time.sleep(1)
            
            pin.close()
            print(f"✓ {pin_name} test PASSED")
        else:
            # Test digital output pin
            print(f"Creating digital output on pin {pin_num}...")
            pin = OutputDevice(pin_num, active_high=True, initial_value=False)
            
            print("Setting pin HIGH...")
            pin.on()
            time.sleep(2)
            
            print("Setting pin LOW...")
            pin.off()
            time.sleep(1)
            
            pin.close()
            print(f"✓ {pin_name} test PASSED")
            
        return True
    except Exception as e:
        print(f"✗ {pin_name} test FAILED: {e}")
        return False

def test_motor_direction(motor_name, in1_pin, in2_pin, ena_pin):
    """Test a motor in both directions"""
    print(f"\n{'='*50}")
    print(f"Testing {motor_name} Full Sequence")
    print(f"{'='*50}")
    
    try:
        in1 = OutputDevice(in1_pin, active_high=True, initial_value=False)
        in2 = OutputDevice(in2_pin, active_high=True, initial_value=False)
        ena = PWMOutputDevice(ena_pin, frequency=1000, initial_value=0.0)
        
        # Forward
        print(f"{motor_name} FORWARD at 50% speed...")
        in1.on()
        in2.off()
        ena.value = 0.5
        time.sleep(3)
        
        # Stop
        print(f"{motor_name} STOP...")
        in1.off()
        in2.off()
        ena.value = 0.0
        time.sleep(1)
        
        # Backward
        print(f"{motor_name} BACKWARD at 50% speed...")
        in1.off()
        in2.on()
        ena.value = 0.5
        time.sleep(3)
        
        # Stop
        print(f"{motor_name} STOP...")
        in1.off()
        in2.off()
        ena.value = 0.0
        
        in1.close()
        in2.close()
        ena.close()
        
        print(f"✓ {motor_name} full test PASSED")
        return True
    except Exception as e:
        print(f"✗ {motor_name} full test FAILED: {e}")
        return False

def main():
    """Run all GPIO tests"""
    print("\n" + "="*50)
    print("L298N Motor Driver GPIO Test")
    print("="*50)
    print("\nThis will test each GPIO pin individually.")
    print("Watch the motor driver board and motors for activity.")
    print("\nPin Configuration:")
    print(f"  Motor A (Left):  IN1={IN1}, IN2={IN2}, ENA={ENA}")
    print(f"  Motor B (Right): IN3={IN3}, IN4={IN4}, ENB={ENB}")
    print("\nPress Ctrl+C to stop at any time.\n")
    
    input("Press ENTER to start individual pin tests...")
    
    results = {}
    
    # Test each pin individually
    print("\n" + "="*60)
    print("PHASE 1: Individual Pin Tests")
    print("="*60)
    
    results['IN1'] = test_pin(IN1, "IN1 (Motor A Direction 1)")
    time.sleep(0.5)
    
    results['IN2'] = test_pin(IN2, "IN2 (Motor A Direction 2)")
    time.sleep(0.5)
    
    results['ENA'] = test_pin(ENA, "ENA (Motor A PWM)", is_pwm=True)
    time.sleep(0.5)
    
    results['IN3'] = test_pin(IN3, "IN3 (Motor B Direction 1)")
    time.sleep(0.5)
    
    results['IN4'] = test_pin(IN4, "IN4 (Motor B Direction 2)")
    time.sleep(0.5)
    
    results['ENB'] = test_pin(ENB, "ENB (Motor B PWM)", is_pwm=True)
    time.sleep(0.5)
    
    # Test full motor sequences
    print("\n" + "="*60)
    print("PHASE 2: Full Motor Tests")
    print("="*60)
    print("\nNow testing complete motor sequences.")
    print("Motors should spin in both directions.\n")
    
    input("Press ENTER to test Motor A (Left)...")
    results['Motor A'] = test_motor_direction("Motor A (Left)", IN1, IN2, ENA)
    time.sleep(1)
    
    input("Press ENTER to test Motor B (Right)...")
    results['Motor B'] = test_motor_direction("Motor B (Right)", IN3, IN4, ENB)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED - Wiring is correct!")
    else:
        print("✗ SOME TESTS FAILED - Check wiring and connections")
        print("\nTroubleshooting:")
        print("1. Verify L298N power supply (5-12V on VCC, 5V on +5V)")
        print("2. Check all GPIO connections match the pin numbers above")
        print("3. Ensure motors are connected to OUT1-OUT2 and OUT3-OUT4")
        print("4. Check for loose wires or bad connections")
        print("5. Verify L298N jumpers are in place for ENA/ENB")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✋ Test interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
