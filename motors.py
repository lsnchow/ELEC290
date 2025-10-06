"""
L298N Motor Driver Controller
Controls two DC motors for a robot car
"""
import time

USE_GPIOD = False
USE_RPIGPIO = False

try:
    import gpiod
    USE_GPIOD = True
    print("Motors: Using gpiod library")
except ImportError:
    try:
        import RPi.GPIO as GPIO
        USE_RPIGPIO = True
        print("Motors: Using RPi.GPIO library")
    except (ImportError, RuntimeError):
        print("Motors: No GPIO library - DUMMY MODE")


class MotorController:
    def __init__(self, ena=17, in1=27, in2=22, enb=18, in3=23, in4=24):
        """
        Initialize L298N Motor Controller
        
        Args:
            ena: Enable pin for Motor A (PWM)
            in1, in2: Control pins for Motor A direction
            enb: Enable pin for Motor B (PWM)
            in3, in4: Control pins for Motor B direction
        """
        self.ena = ena
        self.in1 = in1
        self.in2 = in2
        self.enb = enb
        self.in3 = in3
        self.in4 = in4
        self.dummy_mode = False
        
        if USE_RPIGPIO:
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
        elif USE_GPIOD:
            # TODO: Implement gpiod PWM (more complex)
            print("⚠️  gpiod PWM not implemented yet, using dummy mode")
            self.dummy_mode = True
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
        
        if USE_RPIGPIO:
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
        
        if USE_RPIGPIO:
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
        
        if USE_RPIGPIO:
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
        
        if USE_RPIGPIO:
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
        
        if USE_RPIGPIO:
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
        if USE_RPIGPIO:
            self.pwm_a.stop()
            self.pwm_b.stop()
            GPIO.cleanup([self.ena, self.in1, self.in2, self.enb, self.in3, self.in4])
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
