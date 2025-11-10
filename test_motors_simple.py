#!/usr/bin/env python3
"""
Simple Motor Test - Direct L298N Control
Tests motors with the exact same code as motors.py
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

print("="*60)
print("SIMPLE MOTOR TEST")
print("="*60)
print(f"\nPin Configuration:")
print(f"  Motor A (Left):  IN1={IN1}, IN2={IN2}, ENA={ENA}")
print(f"  Motor B (Right): IN3={IN3}, IN4={IN4}, ENB={ENB}")
print("\nInitializing motors...")

try:
    # Initialize all pins
    in1_a = OutputDevice(IN1, active_high=True, initial_value=False)
    in2_a = OutputDevice(IN2, active_high=True, initial_value=False)
    ena_a = PWMOutputDevice(ENA, frequency=1000, initial_value=0.0)
    
    in1_b = OutputDevice(IN3, active_high=True, initial_value=False)
    in2_b = OutputDevice(IN4, active_high=True, initial_value=False)
    ena_b = PWMOutputDevice(ENB, frequency=1000, initial_value=0.0)
    
    print("✓ Motors initialized successfully!\n")
    
    # Test sequence
    print("="*60)
    print("TEST 1: BOTH MOTORS FORWARD (60% speed)")
    print("="*60)
    print("Motor A (Left):  IN1=HIGH, IN2=LOW, ENA=60%")
    print("Motor B (Right): IN3=HIGH, IN4=LOW, ENB=60%")
    print("Expected: Both motors spin forward, robot moves forward\n")
    
    in1_a.on()
    in2_a.off()
    ena_a.value = 0.6
    
    in1_b.on()
    in2_b.off()
    ena_b.value = 0.6
    
    input("Press ENTER when ready to continue...")
    
    # Stop
    print("\nSTOPPING...")
    in1_a.off()
    in2_a.off()
    ena_a.value = 0.0
    in1_b.off()
    in2_b.off()
    ena_b.value = 0.0
    time.sleep(1)
    
    # Test 2: Backward
    print("\n" + "="*60)
    print("TEST 2: BOTH MOTORS BACKWARD (60% speed)")
    print("="*60)
    print("Motor A (Left):  IN1=LOW, IN2=HIGH, ENA=60%")
    print("Motor B (Right): IN3=LOW, IN4=HIGH, ENB=60%")
    print("Expected: Both motors spin backward, robot moves backward\n")
    
    in1_a.off()
    in2_a.on()
    ena_a.value = 0.6
    
    in1_b.off()
    in2_b.on()
    ena_b.value = 0.6
    
    input("Press ENTER when ready to continue...")
    
    # Stop
    print("\nSTOPPING...")
    in1_a.off()
    in2_a.off()
    ena_a.value = 0.0
    in1_b.off()
    in2_b.off()
    ena_b.value = 0.0
    time.sleep(1)
    
    # Test 3: Left turn
    print("\n" + "="*60)
    print("TEST 3: TURN LEFT (Right motor forward, Left motor backward)")
    print("="*60)
    print("Motor A (Left):  IN1=LOW, IN2=HIGH, ENA=30%")
    print("Motor B (Right): IN3=HIGH, IN4=LOW, ENB=60%")
    print("Expected: Robot spins left\n")
    
    in1_a.off()
    in2_a.on()
    ena_a.value = 0.3
    
    in1_b.on()
    in2_b.off()
    ena_b.value = 0.6
    
    input("Press ENTER when ready to continue...")
    
    # Stop
    print("\nSTOPPING...")
    in1_a.off()
    in2_a.off()
    ena_a.value = 0.0
    in1_b.off()
    in2_b.off()
    ena_b.value = 0.0
    time.sleep(1)
    
    # Test 4: Right turn
    print("\n" + "="*60)
    print("TEST 4: TURN RIGHT (Left motor forward, Right motor backward)")
    print("="*60)
    print("Motor A (Left):  IN1=HIGH, IN2=LOW, ENA=60%")
    print("Motor B (Right): IN3=LOW, IN4=HIGH, ENB=30%")
    print("Expected: Robot spins right\n")
    
    in1_a.on()
    in2_a.off()
    ena_a.value = 0.6
    
    in1_b.off()
    in2_b.on()
    ena_b.value = 0.3
    
    input("Press ENTER when ready to continue...")
    
    # Stop
    print("\nSTOPPING...")
    in1_a.off()
    in2_a.off()
    ena_a.value = 0.0
    in1_b.off()
    in2_b.off()
    ena_b.value = 0.0
    time.sleep(1)
    
    # Test 5: Speed ramp
    print("\n" + "="*60)
    print("TEST 5: SPEED RAMP (0% to 100% forward)")
    print("="*60)
    print("Expected: Motors gradually speed up\n")
    
    in1_a.on()
    in2_a.off()
    in1_b.on()
    in2_b.off()
    
    for speed in range(0, 101, 10):
        speed_val = speed / 100.0
        ena_a.value = speed_val
        ena_b.value = speed_val
        print(f"Speed: {speed}%")
        time.sleep(0.5)
    
    print("\nStopping...")
    ena_a.value = 0.0
    ena_b.value = 0.0
    in1_a.off()
    in2_a.off()
    in1_b.off()
    in2_b.off()
    
    # Cleanup
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nCleaning up GPIO...")
    
    in1_a.close()
    in2_a.close()
    ena_a.close()
    in1_b.close()
    in2_b.close()
    ena_b.close()
    
    print("✓ All tests complete!")
    print("\nDid the motors work? If not, check:")
    print("1. L298N power supply (6-12V on VCC)")
    print("2. ENA and ENB jumpers are IN PLACE")
    print("3. Motors connected to OUT1-OUT2 and OUT3-OUT4")
    print("4. Common ground between Pi and L298N")
    
except KeyboardInterrupt:
    print("\n\n✋ Test interrupted by user")
    print("Cleaning up GPIO...")
    try:
        in1_a.close()
        in2_a.close()
        ena_a.close()
        in1_b.close()
        in2_b.close()
        ena_b.close()
    except:
        pass
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    print("\nCleaning up GPIO...")
    try:
        in1_a.close()
        in2_a.close()
        ena_a.close()
        in1_b.close()
        in2_b.close()
        ena_b.close()
    except:
        pass
