#!/usr/bin/env python3
"""
Quick test to verify Arduino is sending data correctly
Run this to check if Python can receive your Arduino's JSON messages
"""
import serial
import json
import time

# Try common ports
ports = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyUSB1', '/dev/cu.usbserial-0001', '/dev/cu.usbmodem*']

print("🔍 Testing Arduino Serial Communication\n")
print("Looking for Arduino on common ports...")

serial_port = None
for port in ports:
    try:
        print(f"  Trying {port}...", end=" ")
        ser = serial.Serial(port, 9600, timeout=2)
        time.sleep(2)  # Wait for Arduino to reset
        print("✓ Connected!")
        serial_port = ser
        break
    except (FileNotFoundError, serial.SerialException) as e:
        print(f"✗ Not available")

if not serial_port:
    print("\n❌ Could not find Arduino on any port!")
    print("\nTroubleshooting:")
    print("1. Check USB cable is connected")
    print("2. Close Arduino IDE Serial Monitor")
    print("3. Run: ls /dev/tty* | grep -E 'USB|ACM' to find your port")
    exit(1)

print(f"\n✅ Connected to Arduino on {serial_port.port}")
print("Reading data for 10 seconds...\n")

lines_received = 0
valid_json = 0
start_time = time.time()

try:
    while time.time() - start_time < 10:
        if serial_port.in_waiting > 0:
            line = serial_port.readline().decode('utf-8', errors='ignore').strip()
            
            if not line:
                continue
            
            lines_received += 1
            print(f"📥 Raw data: {line}")
            
            # Try to parse JSON
            try:
                data = json.loads(line)
                valid_json += 1
                
                # Extract values
                accel_x = data.get('accelX', 'N/A')
                accel_y = data.get('accelY', 'N/A')
                accel_z = data.get('accelZ', 'N/A')
                gyro_x = data.get('gyroX', 'N/A')
                gyro_y = data.get('gyroY', 'N/A')
                gyro_z = data.get('gyroZ', 'N/A')
                temp = data.get('tempC', data.get('temp', 'N/A'))
                dist = data.get('distCM', data.get('dist', 'N/A'))
                
                print(f"✓ Parsed successfully!")
                print(f"  📊 Accel: X={accel_x}, Y={accel_y}, Z={accel_z} m/s²")
                print(f"  🔄 Gyro:  X={gyro_x}, Y={gyro_y}, Z={gyro_z} rad/s")
                print(f"  🌡️  Temp:  {temp}°C")
                print(f"  📏 Dist:  {dist} cm")
                print()
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed: {e}")
                print()
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\n⏹️  Stopped by user")

serial_port.close()

print("\n" + "="*60)
print(f"📊 Summary:")
print(f"   Lines received: {lines_received}")
print(f"   Valid JSON:     {valid_json}")
print(f"   Success rate:   {(valid_json/lines_received*100) if lines_received > 0 else 0:.1f}%")
print("="*60)

if valid_json > 0:
    print("\n✅ Arduino communication is working perfectly!")
    print("   Your app.py should now receive data correctly.")
else:
    print("\n⚠️  No valid JSON received!")
    print("   Check your Arduino sketch is uploaded correctly.")
