"""
Arduino Serial Communication
Reads sensor data (gas, temperature, distance) from Arduino via serial port
"""
import serial
import json
import threading
import time


class ArduinoSerial:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        """
        Initialize Arduino serial communication
        
        Args:
            port: Serial port (default: /dev/ttyUSB0, could be /dev/ttyACM0)
            baudrate: Baud rate (default: 9600)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        self.thread = None
        
        # Sensor data
        self.gas_level = 0
        self.temperature = 0
        self.distance = 0
        self.last_update = time.time()
        
        try:
            self.serial = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            print(f"✓ Arduino connected on {port}")
        except Exception as e:
            print(f"⚠️  Could not connect to Arduino: {e}")
            print("   Sensor data will be simulated")
    
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
        while self.running:
            try:
                if self.serial.in_waiting > 0:
                    line = self.serial.readline().decode('utf-8').strip()
                    
                    # Expected format: {"gas":450,"temp":25.5,"dist":10.2}
                    try:
                        data = json.loads(line)
                        self.gas_level = data.get('gas', 0)
                        self.temperature = data.get('temp', 0)
                        self.distance = data.get('dist', 0)
                        self.last_update = time.time()
                    except json.JSONDecodeError:
                        # Try comma-separated format: gas,temp,dist
                        parts = line.split(',')
                        if len(parts) == 3:
                            self.gas_level = float(parts[0])
                            self.temperature = float(parts[1])
                            self.distance = float(parts[2])
                            self.last_update = time.time()
            except Exception as e:
                print(f"Arduino read error: {e}")
            
            time.sleep(0.1)
    
    def _simulate_data(self):
        """Simulate sensor data when Arduino not connected"""
        import random
        while self.running:
            self.gas_level = random.randint(300, 500)
            self.temperature = round(random.uniform(20, 30), 1)
            self.distance = round(random.uniform(5, 50), 1)
            self.last_update = time.time()
            time.sleep(0.5)
    
    def get_data(self):
        """Get current sensor data"""
        return {
            'gas': self.gas_level,
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
