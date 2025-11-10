"""
L298N Motor Driver Controller
Controls two DC motors for a robot car
"""
import time

USE_GPIOZERO = False
USE_RPIGPIO = False

try:
    from gpiozero import OutputDevice, PWMOutputDevice
    USE_GPIOZERO = True
    print("Motors: Using gpiozero library (Raspberry Pi 5)")
except ImportError:
    try:
        import RPi.GPIO as GPIO
        USE_RPIGPIO = True
        print("Motors: Using RPi.GPIO library")
    except (ImportError, RuntimeError):
        print("Motors: No GPIO library - DUMMY MODE")


class MotorController:
    def __init__(self, ena=22, in1=17, in2=27, enb=25, in3=23, in4=24):
        """
        Initialize L298N Motor Controller
        
        Args:
            ena: Enable pin for Motor A (PWM) - Default 22
            in1, in2: Control pins for Motor A direction - Default 17, 27
            enb: Enable pin for Motor B (PWM) - Default 25
            in3, in4: Control pins for Motor B direction - Default 23, 24
        
        Note: Updated pinout for gpiozero compatibility:
            Motor A (Left):  IN1=17, IN2=27, ENA=22 (PWM)
            Motor B (Right): IN1=23, IN2=24, ENB=25 (PWM)
        """
        self.dummy_mode = False
        
        # Store pin numbers for RPi.GPIO
        self.ena = ena
        self.in1 = in1
        self.in2 = in2
        self.enb = enb
        self.in3 = in3
        self.in4 = in4
        
        if USE_GPIOZERO:
            try:
                # Motor A (Left) using gpiozero
                self.in1_a = OutputDevice(in1, active_high=True, initial_value=False)
                self.in2_a = OutputDevice(in2, active_high=True, initial_value=False)
                self.ena_a = PWMOutputDevice(ena, frequency=1000, initial_value=0.0)
                
                # Motor B (Right) using gpiozero
                self.in1_b = OutputDevice(in3, active_high=True, initial_value=False)
                self.in2_b = OutputDevice(in4, active_high=True, initial_value=False)
                self.ena_b = PWMOutputDevice(enb, frequency=1000, initial_value=0.0)
                
                print(f"✓ Motors initialized (gpiozero - Pi 5)")
                print(f"  Motor A (Left):  IN1={in1}, IN2={in2}, ENA={ena}")
                print(f"  Motor B (Right): IN1={in3}, IN2={in4}, ENB={enb}")
            except Exception as e:
                print(f"⚠️  gpiozero init failed: {e}, using dummy mode")
                self.dummy_mode = True
        elif USE_RPIGPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup motor pins
            GPIO.setup([ena, in1, in2, enb, in3, in4], GPIO.OUT)
            
            # Setup PWM for speed control (1000 Hz)
            self.pwm_a = GPIO.PWM(ena, 1000)
            self.pwm_b = GPIO.PWM(enb, 1000)
            self.pwm_a.start(0)
            self.pwm_b.start(0)
            
            print(f"✓ Motors initialized (RPi.GPIO)")
        else:
            self.dummy_mode = True
            print("⚠️  Motors in DUMMY MODE")
        
        self.current_speed = 0
        self.current_direction = "stop"
    
    def forward(self, speed=50):
        """Move forward at given speed (0-100)"""
        if self.dummy_mode:
            print(f"DUMMY: Forward at {speed}%")
            self.current_direction = "forward"
            self.current_speed = speed
            return
        
        speed_fraction = speed / 100.0  # Convert 0-100 to 0.0-1.0
        
        if USE_GPIOZERO:
            # Motor A forward
            self.in1_a.on()
            self.in2_a.off()
            self.ena_a.value = speed_fraction
            
            # Motor B forward
            self.in1_b.on()
            self.in2_b.off()
            self.ena_b.value = speed_fraction
        elif USE_RPIGPIO:
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)
            GPIO.output(self.in3, GPIO.HIGH)
            GPIO.output(self.in4, GPIO.LOW)
            self.pwm_a.ChangeDutyCycle(speed)
            self.pwm_b.ChangeDutyCycle(speed)
        
        self.current_direction = "forward"
        self.current_speed = speed
    
    def backward(self, speed=50):
        """Move backward at given speed (0-100)"""
        if self.dummy_mode:
            print(f"DUMMY: Backward at {speed}%")
            self.current_direction = "backward"
            self.current_speed = speed
            return
        
        speed_fraction = speed / 100.0
        
        if USE_GPIOZERO:
            # Motor A backward
            self.in1_a.off()
            self.in2_a.on()
            self.ena_a.value = speed_fraction
            
            # Motor B backward
            self.in1_b.off()
            self.in2_b.on()
            self.ena_b.value = speed_fraction
        elif USE_RPIGPIO:
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.HIGH)
            GPIO.output(self.in3, GPIO.LOW)
            GPIO.output(self.in4, GPIO.HIGH)
            self.pwm_a.ChangeDutyCycle(speed)
            self.pwm_b.ChangeDutyCycle(speed)
        
        self.current_direction = "backward"
        self.current_speed = speed
    
    def left(self, speed=50):
        """Turn left (left motor slower/stopped)"""
        if self.dummy_mode:
            print(f"DUMMY: Left at {speed}%")
            self.current_direction = "left"
            self.current_speed = speed
            return
        
        speed_fraction = speed / 100.0
        
        if USE_GPIOZERO:
            # Left motor backward/slow
            self.in1_a.off()
            self.in2_a.on()
            self.ena_a.value = speed_fraction * 0.5  # Half speed
            
            # Right motor forward
            self.in1_b.on()
            self.in2_b.off()
            self.ena_b.value = speed_fraction
        elif USE_RPIGPIO:
            # Right motor forward, left motor slower/backward
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.HIGH)
            GPIO.output(self.in3, GPIO.HIGH)
            GPIO.output(self.in4, GPIO.LOW)
            self.pwm_a.ChangeDutyCycle(speed // 2)
            self.pwm_b.ChangeDutyCycle(speed)
        
        self.current_direction = "left"
        self.current_speed = speed
    
    def right(self, speed=50):
        """Turn right (right motor slower/stopped)"""
        if self.dummy_mode:
            print(f"DUMMY: Right at {speed}%")
            self.current_direction = "right"
            self.current_speed = speed
            return
        
        speed_fraction = speed / 100.0
        
        if USE_GPIOZERO:
            # Left motor forward
            self.in1_a.on()
            self.in2_a.off()
            self.ena_a.value = speed_fraction
            
            # Right motor backward/slow
            self.in1_b.off()
            self.in2_b.on()
            self.ena_b.value = speed_fraction * 0.5  # Half speed
        elif USE_RPIGPIO:
            # Left motor forward, right motor slower/backward
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)
            GPIO.output(self.in3, GPIO.LOW)
            GPIO.output(self.in4, GPIO.HIGH)
            self.pwm_a.ChangeDutyCycle(speed)
            self.pwm_b.ChangeDutyCycle(speed // 2)
        
        self.current_direction = "right"
        self.current_speed = speed
    
    def stop(self):
        """Stop all motors"""
        if self.dummy_mode:
            print("DUMMY: Stop")
            self.current_direction = "stop"
            self.current_speed = 0
            return
        
        if USE_GPIOZERO:
            # Brake (both high for active braking)
            self.in1_a.on()
            self.in2_a.on()
            self.ena_a.value = 0.0
            
            self.in1_b.on()
            self.in2_b.on()
            self.ena_b.value = 0.0
        elif USE_RPIGPIO:
            GPIO.output([self.in1, self.in2, self.in3, self.in4], GPIO.LOW)
            self.pwm_a.ChangeDutyCycle(0)
            self.pwm_b.ChangeDutyCycle(0)
        
        self.current_direction = "stop"
        self.current_speed = 0
    
    def get_status(self):
        """Get current motor status"""
        return {
            "direction": self.current_direction,
            "speed": self.current_speed
        }
    
    def cleanup(self):
        """Clean up GPIO"""
        self.stop()
        if USE_GPIOZERO and not self.dummy_mode:
            try:
                self.ena_a.close()
                self.in1_a.close()
                self.in2_a.close()
                self.ena_b.close()
                self.in1_b.close()
                self.in2_b.close()
            except Exception as e:
                print(f"Cleanup warning: {e}")
        elif USE_RPIGPIO:
            self.pwm_a.stop()
            self.pwm_b.stop()
            GPIO.cleanup()
        print("Motors cleanup complete")


# Test code
if __name__ == "__main__":
    print("Testing Motor Controller")
    print("Press Ctrl+C to exit\n")
    
    motors = MotorController()
    
    try:
        print("Forward...")
        motors.forward(60)
        time.sleep(2)
        
        print("Left...")
        motors.left(60)
        time.sleep(1)
        
        print("Right...")
        motors.right(60)
        time.sleep(1)
        
        print("Backward...")
        motors.backward(60)
        time.sleep(2)
        
        print("Stop")
        motors.stop()
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        motors.cleanup()
        print("Test complete")
