#!/usr/bin/env python3
"""
Quick Arduino reconnection fix
Use this if Arduino was unplugged and now shows zero values
"""
import sys
import time

print("🔧 Arduino Reconnection Fix\n")
print("This will:")
print("1. Check if Arduino is sending data")
print("2. Help you reconnect if needed\n")

# First, let's check if Arduino is actually sending data
print("Step 1: Testing Arduino Serial Output")
print("-" * 60)

try:
    import serial
    import serial.tools.list_ports
    
    # List all ports
    ports = list(serial.tools.list_ports.comports())
    print(f"\nFound {len(ports)} serial port(s):")
    for port in ports:
        print(f"  - {port.device}: {port.description}")
    
    if not ports:
        print("\n❌ No serial ports found!")
        print("\nSolutions:")
        print("1. Check USB cable is plugged in")
        print("2. Try a different USB port")
        print("3. Check if Arduino has power (LED on)")
        sys.exit(1)
    
    # Try to connect to most likely port
    likely_ports = [p.device for p in ports if 'USB' in p.device or 'ACM' in p.device]
    
    if not likely_ports:
        print("\n⚠️  No USB/ACM ports found, trying all ports...")
        likely_ports = [p.device for p in ports]
    
    print(f"\nStep 2: Testing ports for Arduino data")
    print("-" * 60)
    
    for port_name in likely_ports:
        print(f"\n📡 Testing {port_name}...")
        try:
            ser = serial.Serial(port_name, 9600, timeout=2)
            print(f"  ✓ Opened successfully")
            print(f"  ⏳ Waiting 3 seconds for Arduino to reset...")
            time.sleep(3)
            
            print(f"  📥 Reading data (10 seconds)...")
            start = time.time()
            lines = 0
            valid_json = 0
            
            while time.time() - start < 10:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        lines += 1
                        print(f"    [{lines}] {line}")
                        
                        # Check if it's valid JSON with our expected format
                        if 'accelX' in line and 'gyroX' in line:
                            valid_json += 1
            
            ser.close()
            
            print(f"\n  📊 Results:")
            print(f"    Total lines: {lines}")
            print(f"    Valid JSON: {valid_json}")
            
            if valid_json > 0:
                print(f"\n✅ SUCCESS! Arduino is working on {port_name}")
                print(f"\nNext steps:")
                print(f"1. Update config.py: ARDUINO_PORT = '{port_name}'")
                print(f"2. Restart app.py")
                print(f"\nOr just restart app.py - it has auto-port detection!")
                sys.exit(0)
            elif lines > 0:
                print(f"\n⚠️  Arduino is sending data but not in expected format")
                print(f"    Check if correct sketch is uploaded")
            else:
                print(f"\n✗ No data received from {port_name}")
                
        except serial.SerialException as e:
            print(f"  ✗ Could not open: {e}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("❌ No working Arduino found on any port")
    print("\nTroubleshooting:")
    print("1. Open Arduino IDE Serial Monitor (9600 baud)")
    print("2. Check if you see JSON like: {\"accelX\":-0.31,...}")
    print("3. If yes → Close Serial Monitor and try again")
    print("4. If no → Re-upload arduino_sensors.ino sketch")
    print("5. Make sure Arduino IDE Serial Monitor is CLOSED")
    
except ImportError:
    print("❌ pyserial not installed!")
    print("Run: pip3 install pyserial")
    sys.exit(1)
