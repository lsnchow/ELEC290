"""
HC-SR04 Ultrasonic Sensor Module
Measures distance using GPIO pins with proper timing
Compatible with Raspberry Pi 5 using gpiod
"""
import time
import threading
import os

USE_GPIOD = False
USE_RPIGPIO = False

try:
    import gpiod
    from gpiod.line import Direction, Value
    USE_GPIOD = True
    print("Using gpiod library")
except ImportError:
    try:
        import RPi.GPIO as GPIO
        USE_RPIGPIO = True
        print("Using RPi.GPIO library")
    except (ImportError, RuntimeError):
        print("Warning: No GPIO library available. Ultrasonic sensor will return dummy data.")


class UltrasonicSensor:
    def __init__(self, trig_pin=23, echo_pin=24):
        """
        Initialize the HC-SR04 ultrasonic sensor
        
        Args:
            trig_pin: GPIO pin number for trigger (default: 23)
            echo_pin: GPIO pin number for echo (default: 24)
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.distance = 0
        self.running = False
        self.dummy_mode = False
        
        if USE_GPIOD:
            # Use gpiod for Raspberry Pi 5
            # Try different chip numbers (Pi 5 uses gpiochip4->gpiochip0, older models use gpiochip0)
            chip_found = False
            for chip_num in [4, 0, 1, 2, 3]:
                try:
                    chip_path = f'/dev/gpiochip{chip_num}'
                    print(f"Trying {chip_path}...")
                    self.chip = gpiod.Chip(chip_path)
                    chip_found = True
                    print(f"✓ Using gpiochip{chip_num}")
                    break
                except (FileNotFoundError, PermissionError, OSError) as e:
                    print(f"  Failed: {e}")
                    continue
            
            if not chip_found:
                print("⚠️  Could not access any GPIO chip with gpiod")
                print("   Falling back to dummy mode")
                self.dummy_mode = True
        
        if USE_GPIOD and hasattr(self, 'chip') and not self.dummy_mode:
            try:
                self.trig_line = self.chip.get_line(self.trig_pin)
                self.echo_line = self.chip.get_line(self.echo_pin)
                
                self.trig_line.request(consumer="ultrasonic", type=gpiod.LINE_REQ_DIR_OUT)
                self.echo_line.request(consumer="ultrasonic", type=gpiod.LINE_REQ_DIR_IN)
                
                self.trig_line.set_value(0)
                print(f"Ultrasonic sensor initialized (gpiod) on TRIG={trig_pin}, ECHO={echo_pin}")
            except Exception as e:
                print(f"Failed to initialize GPIO lines: {e}")
                print("Falling back to dummy mode")
                self.dummy_mode = True
        elif USE_RPIGPIO:
            # Use RPi.GPIO for older Pi models
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.trig_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trig_pin, False)
            print(f"Ultrasonic sensor initialized (RPi.GPIO) on TRIG={trig_pin}, ECHO={echo_pin}")
        else:
            # No GPIO library available - use dummy mode
            self.dummy_mode = True
            print(f"⚠️  Ultrasonic sensor in DUMMY MODE (no GPIO library available)")
            print(f"   Install gpiod: pip install gpiod")
            print(f"   Sensor will return simulated distance data")
        
        time.sleep(0.1)
    
    def measure_distance(self):
        """
        Measure distance in centimeters
        
        Returns:
            float: Distance in cm, or -1 if measurement failed
        """
        # Return dummy data if no GPIO library
        if self.dummy_mode:
            import random
            return round(random.uniform(20, 100), 1)
        
        try:
            if USE_GPIOD:
                # Send 10us pulse to trigger
                self.trig_line.set_value(1)
                time.sleep(0.00001)  # 10 microseconds
                self.trig_line.set_value(0)
                
                # Wait for echo to start (with timeout)
                pulse_start = time.time()
                timeout = pulse_start + 0.1  # 100ms timeout
                
                while self.echo_line.get_value() == 0:
                    pulse_start = time.time()
                    if pulse_start > timeout:
                        return -1
                
                # Wait for echo to end (with timeout)
                pulse_end = time.time()
                timeout = pulse_end + 0.1
                
                while self.echo_line.get_value() == 1:
                    pulse_end = time.time()
                    if pulse_end > timeout:
                        return -1
            else:
                # RPi.GPIO version
                GPIO.output(self.trig_pin, True)
                time.sleep(0.00001)
                GPIO.output(self.trig_pin, False)
                
                pulse_start = time.time()
                timeout = pulse_start + 0.1
                
                while GPIO.input(self.echo_pin) == 0:
                    pulse_start = time.time()
                    if pulse_start > timeout:
                        return -1
                
                pulse_end = time.time()
                timeout = pulse_end + 0.1
                
                while GPIO.input(self.echo_pin) == 1:
                    pulse_end = time.time()
                    if pulse_end > timeout:
                        return -1
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            # Speed of sound is 343 m/s or 34300 cm/s
            # Distance = (Time × Speed) / 2 (divided by 2 for round trip)
            distance = (pulse_duration * 34300) / 2
            
            # Valid range for HC-SR04 is 2cm to 400cm
            if 2 <= distance <= 400:
                return round(distance, 1)
            else:
                return -1
                
        except Exception as e:
            print(f"Error measuring distance: {e}")
            return -1
    
    def start_continuous_reading(self, interval=0.1):
        """
        Start continuous distance reading in background thread
        
        Args:
            interval: Time between measurements in seconds (default: 0.1)
        """
        self.running = True
        
        def read_loop():
            while self.running:
                measurement = self.measure_distance()
                if measurement != -1:
                    self.distance = measurement
                time.sleep(interval)
        
        self.thread = threading.Thread(target=read_loop, daemon=True)
        self.thread.start()
        print("Continuous distance reading started")
    
    def stop_continuous_reading(self):
        """Stop continuous distance reading"""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1)
        print("Continuous distance reading stopped")
    
    def get_distance(self):
        """
        Get the latest distance reading
        
        Returns:
            float: Distance in cm
        """
        return self.distance
    
    def cleanup(self):
        """Clean up GPIO pins"""
        self.stop_continuous_reading()
        if self.dummy_mode:
            print("Dummy mode cleanup complete")
        elif USE_GPIOD:
            if hasattr(self, 'trig_line'):
                self.trig_line.release()
            if hasattr(self, 'echo_line'):
                self.echo_line.release()
            if hasattr(self, 'chip'):
                self.chip.close()
            print("GPIO cleanup complete (gpiod)")
        elif USE_RPIGPIO:
            GPIO.cleanup([self.trig_pin, self.echo_pin])
            print("GPIO cleanup complete (RPi.GPIO)")


# Test code
if __name__ == "__main__":
    print("Testing HC-SR04 Ultrasonic Sensor")
    print("Press Ctrl+C to exit\n")
    
    sensor = UltrasonicSensor()
    
    try:
        sensor.start_continuous_reading(interval=0.2)
        
        while True:
            distance = sensor.get_distance()
            if distance > 0:
                print(f"Distance: {distance:.1f} cm")
            else:
                print("Out of range or error")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        sensor.cleanup()
        print("Test complete")
