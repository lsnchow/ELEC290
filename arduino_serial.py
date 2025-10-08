"""
Arduino Serial Communication
Reads sensor data (gas, temperature, distance) from Arduino via serial port
"""
import serial
import json
import threading
import time


class ArduinoSerial:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, debug=False):
        """
        Initialize Arduino serial communication
        
        Args:
            port: Serial port (default: /dev/ttyUSB0, could be /dev/ttyACM0)
            baudrate: Baud rate (default: 9600)
            debug: Enable debug output (default: False)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        self.thread = None
        self.debug = debug
        
        # Sensor data (MPU6050 + ultrasonic)
        self.accel_x = 0
        self.accel_y = 0
        self.accel_z = 0
        self.gyro_x = 0
        self.gyro_y = 0
        self.gyro_z = 0
        self.temperature = 0
        self.distance = 0
        self.last_update = time.time()
        
        # Try multiple common ports if default fails
        ports_to_try = [port, '/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyUSB1']
        
        for try_port in ports_to_try:
            try:
                if self.debug:
                    print(f"Trying to connect to {try_port}...")
                self.serial = serial.Serial(try_port, baudrate, timeout=1)
                time.sleep(2)  # Wait for Arduino to reset
                print(f"✓ Arduino connected on {try_port}")
                self.port = try_port  # Update to actual port used
                return
            except FileNotFoundError:
                if self.debug:
                    print(f"  Port {try_port} not found")
                continue
            except serial.SerialException as e:
                if self.debug:
                    print(f"  Could not open {try_port}: {e}")
                continue
            except Exception as e:
                if self.debug:
                    print(f"  Unexpected error with {try_port}: {e}")
                continue
        
        # If we get here, none of the ports worked
        print(f"⚠️  Could not connect to Arduino on any port")
        print("   Tried: " + ", ".join(ports_to_try))
        print("   Sensor data will be simulated")
        print("\nTroubleshooting:")
        print("  1. Check if Arduino is plugged in: ls /dev/tty* | grep -E 'USB|ACM'")
        print("  2. Verify Arduino sketch is uploaded")
        print("  3. Close Arduino IDE Serial Monitor if open")
        print("  4. Run: python3 debug_arduino.py")
    
    def start(self):
        """Start reading data in background thread"""
        if self.serial is None:
            # Simulated mode
            self.running = True
            self.thread = threading.Thread(target=self._simulate_data, daemon=True)
            self.thread.start()
            print("Arduino: Running in simulation mode")
        else:
            self.running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            print("Arduino: Started reading sensor data")
    
    def _read_loop(self):
        """Background thread to read serial data"""
        lines_read = 0
        last_debug_time = time.time()
        
        while self.running:
            try:
                if self.serial.in_waiting > 0:
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line:  # Empty line
                        continue
                    
                    if self.debug:
                        print(f"[Arduino] Raw: {repr(line)}")
                    
                    # Expected format: {"accelX":X,"accelY":Y,"accelZ":Z,"gyroX":X,"gyroY":Y,"gyroZ":Z,"temp":T,"dist":D}
                    try:
                        data = json.loads(line)
                        self.accel_x = data.get('accelX', 0)
                        self.accel_y = data.get('accelY', 0)
                        self.accel_z = data.get('accelZ', 0)
                        self.gyro_x = data.get('gyroX', 0)
                        self.gyro_y = data.get('gyroY', 0)
                        self.gyro_z = data.get('gyroZ', 0)
                        self.temperature = data.get('temp', 0)
                        self.distance = data.get('dist', 0)
                        self.last_update = time.time()
                        lines_read += 1
                        
                        if self.debug:
                            print(f"[Arduino] Parsed: accel=({self.accel_x:.2f},{self.accel_y:.2f},{self.accel_z:.2f}), "
                                  f"gyro=({self.gyro_x:.2f},{self.gyro_y:.2f},{self.gyro_z:.2f}), "
                                  f"temp={self.temperature:.1f}, dist={self.distance:.1f}")
                            
                    except json.JSONDecodeError as e:
                        if self.debug:
                            print(f"[Arduino] JSON error: {e}")
                        
                        # Try comma-separated format: accelX,accelY,accelZ,gyroX,gyroY,gyroZ,temp,dist
                        try:
                            parts = line.split(',')
                            if len(parts) == 8:
                                self.accel_x = float(parts[0])
                                self.accel_y = float(parts[1])
                                self.accel_z = float(parts[2])
                                self.gyro_x = float(parts[3])
                                self.gyro_y = float(parts[4])
                                self.gyro_z = float(parts[5])
                                self.temperature = float(parts[6])
                                self.distance = float(parts[7])
                                self.last_update = time.time()
                                lines_read += 1
                                
                                if self.debug:
                                    print(f"[Arduino] CSV parsed: accel=({self.accel_x:.2f},{self.accel_y:.2f},{self.accel_z:.2f}), "
                                          f"gyro=({self.gyro_x:.2f},{self.gyro_y:.2f},{self.gyro_z:.2f}), "
                                          f"temp={self.temperature:.1f}, dist={self.distance:.1f}")
                        except (ValueError, IndexError) as parse_error:
                            if self.debug:
                                print(f"[Arduino] Could not parse: {parse_error}")
                
                # Debug output every 5 seconds
                if self.debug and time.time() - last_debug_time > 5:
                    print(f"[Arduino] Status: {lines_read} lines read, last update {time.time() - self.last_update:.1f}s ago")
                    last_debug_time = time.time()
                    
            except Exception as e:
                print(f"[Arduino] Read error: {e}")
                if self.debug:
                    import traceback
                    traceback.print_exc()
            
            time.sleep(0.1)
    
    def _simulate_data(self):
        """Simulate sensor data when Arduino not connected"""
        import random
        while self.running:
            self.accel_x = round(random.uniform(-2, 2), 2)
            self.accel_y = round(random.uniform(-2, 2), 2)
            self.accel_z = round(random.uniform(9, 11), 2)  # ~9.8 m/s² gravity
            self.gyro_x = round(random.uniform(-0.5, 0.5), 2)
            self.gyro_y = round(random.uniform(-0.5, 0.5), 2)
            self.gyro_z = round(random.uniform(-0.5, 0.5), 2)
            self.temperature = round(random.uniform(20, 30), 1)
            self.distance = round(random.uniform(5, 50), 1)
            self.last_update = time.time()
            time.sleep(0.5)
    
    def get_data(self):
        """Get current sensor data"""
        return {
            'accelX': self.accel_x,
            'accelY': self.accel_y,
            'accelZ': self.accel_z,
            'gyroX': self.gyro_x,
            'gyroY': self.gyro_y,
            'gyroZ': self.gyro_z,
            'temperature': self.temperature,
            'distance': self.distance,
            'timestamp': self.last_update
        }
    
    def stop(self):
        """Stop reading data"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.serial:
            self.serial.close()
        print("Arduino: Stopped")


# Test code
if __name__ == "__main__":
    print("Testing Arduino Serial Communication")
    print("Press Ctrl+C to exit\n")
    
    arduino = ArduinoSerial()
    arduino.start()
    
    try:
        while True:
            data = arduino.get_data()
            print(f"Gas: {data['gas']}, Temp: {data['temperature']}°C, Distance: {data['distance']}cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        arduino.stop()
        print("Test complete")
