#!/usr/bin/env python3
"""
Arduino Serial Debugger
Run this on your Raspberry Pi to diagnose Arduino communication issues
"""
import serial
import serial.tools.list_ports
import sys
import time

def list_serial_ports():
    """List all available serial ports"""
    print("\n" + "="*60)
    print("STEP 1: Checking for available serial ports...")
    print("="*60)
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No serial ports found!")
        print("\nTroubleshooting:")
        print("  1. Is the Arduino plugged in via USB?")
        print("  2. Try a different USB port")
        print("  3. Try a different USB cable (some are power-only)")
        return []
    
    print(f"\n✓ Found {len(ports)} serial port(s):\n")
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Hardware ID: {port.hwid}")
        print()
    
    return [port.device for port in ports]

def test_port(port, baudrate=9600):
    """Test reading from a specific port"""
    print("\n" + "="*60)
    print(f"STEP 2: Testing port {port} at {baudrate} baud...")
    print("="*60)
    
    try:
        # Try to open the port
        ser = serial.Serial(port, baudrate, timeout=2)
        print(f"✓ Successfully opened {port}")
        print("  Waiting 2 seconds for Arduino to reset...")
        time.sleep(2)
        
        # Try to read some lines
        print("\nAttempting to read data (15 seconds)...")
        print("-" * 60)
        
        lines_read = 0
        start_time = time.time()
        
        while time.time() - start_time < 15:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        lines_read += 1
                        print(f"[{lines_read}] RAW: {repr(line)}")
                        
                        # Try to parse as JSON
                        import json
                        try:
                            data = json.loads(line)
                            print(f"     ✓ Valid JSON: {data}")
                        except json.JSONDecodeError as e:
                            print(f"     ⚠️  Not valid JSON: {e}")
                        print()
                except Exception as e:
                    print(f"     ❌ Error reading line: {e}")
            
            time.sleep(0.1)
        
        ser.close()
        
        if lines_read == 0:
            print("\n❌ No data received!")
            print("\nPossible issues:")
            print("  1. Arduino sketch not uploaded")
            print("  2. Wrong baud rate (should be 9600)")
            print("  3. Arduino Serial.begin() not called")
            print("  4. Arduino crashed/stuck in loop")
            print("  5. Serial Monitor in Arduino IDE is open (close it!)")
            return False
        else:
            print(f"\n✓ Successfully read {lines_read} lines")
            return True
            
    except serial.SerialException as e:
        print(f"\n❌ Could not open port: {e}")
        print("\nPossible issues:")
        print("  1. Port is already in use (close Arduino IDE Serial Monitor)")
        print("  2. Insufficient permissions (try: sudo usermod -a -G dialout $USER)")
        print("  3. Wrong port selected")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def check_permissions():
    """Check if user has permission to access serial ports"""
    print("\n" + "="*60)
    print("STEP 3: Checking permissions...")
    print("="*60)
    
    import os
    import grp
    
    try:
        # Check if user is in dialout group
        groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
        print(f"\nYour groups: {', '.join(groups)}")
        
        if 'dialout' in groups or 'uucp' in groups:
            print("✓ You have serial port permissions")
        else:
            print("\n⚠️  You may not have serial port permissions!")
            print("\nTo fix, run:")
            print("  sudo usermod -a -G dialout $USER")
            print("  (then log out and back in)")
    except Exception as e:
        print(f"Could not check permissions: {e}")

def main():
    print("\n" + "="*60)
    print("  ARDUINO SERIAL DEBUGGER")
    print("="*60)
    
    # Step 1: List ports
    ports = list_serial_ports()
    
    if not ports:
        print("\n❌ Cannot continue without any serial ports")
        sys.exit(1)
    
    # Step 2: Test each port
    print("\n" + "="*60)
    print("Testing each port...")
    print("="*60)
    
    working_ports = []
    for port in ports:
        if test_port(port):
            working_ports.append(port)
    
    # Step 3: Check permissions
    check_permissions()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if working_ports:
        print(f"\n✓ Working port(s): {', '.join(working_ports)}")
        print(f"\nUpdate config.py to use: ARDUINO_PORT = '{working_ports[0]}'")
    else:
        print("\n❌ No working ports found")
        print("\nDEBUGGING CHECKLIST:")
        print("  [ ] Arduino is plugged in via USB")
        print("  [ ] USB cable is data-capable (not just power)")
        print("  [ ] Arduino sketch is uploaded correctly")
        print("  [ ] Baud rate is 9600 in Arduino sketch")
        print("  [ ] Arduino IDE Serial Monitor is CLOSED")
        print("  [ ] You have serial port permissions (dialout group)")
        print("  [ ] Arduino is not frozen/crashed")
        print("\nTo test Arduino independently:")
        print("  1. Open Arduino IDE")
        print("  2. Tools → Serial Monitor")
        print("  3. Set baud rate to 9600")
        print("  4. You should see JSON data like: {\"gas\":450,\"temp\":25.5,\"dist\":10.2}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
