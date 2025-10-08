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
            # gpiod implementation for Raspberry Pi 5
            try:
                self.chip = gpiod.Chip('gpiochip4')  # Pi 5 uses gpiochip4
                
                # Request GPIO lines
                self.line_ena = self.chip.get_line(ena)
                self.line_in1 = self.chip.get_line(in1)
                self.line_in2 = self.chip.get_line(in2)
                self.line_enb = self.chip.get_line(enb)
                self.line_in3 = self.chip.get_line(in3)
                self.line_in4 = self.chip.get_line(in4)
                
                # Configure as outputs
                self.line_ena.request(consumer="motor_ena", type=gpiod.LINE_REQ_DIR_OUT)
                self.line_in1.request(consumer="motor_in1", type=gpiod.LINE_REQ_DIR_OUT)
                self.line_in2.request(consumer="motor_in2", type=gpiod.LINE_REQ_DIR_OUT)
                self.line_enb.request(consumer="motor_enb", type=gpiod.LINE_REQ_DIR_OUT)
                self.line_in3.request(consumer="motor_in3", type=gpiod.LINE_REQ_DIR_OUT)
                self.line_in4.request(consumer="motor_in4", type=gpiod.LINE_REQ_DIR_OUT)
                
                # Start with motors off
                self.line_ena.set_value(0)
                self.line_enb.set_value(0)
                
                # Software PWM simulation (no hardware PWM on all pins)
                self._pwm_duty_a = 0
                self._pwm_duty_b = 0
                
                print(f"✓ Motors initialized (gpiod on Pi 5)")
            except Exception as e:
                print(f"⚠️  gpiod init failed: {e}, using dummy mode")
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
        elif USE_GPIOD:
            # Forward: IN1=HIGH, IN2=LOW, IN3=HIGH, IN4=LOW
            self.line_in1.set_value(1)
            self.line_in2.set_value(0)
            self.line_in3.set_value(1)
            self.line_in4.set_value(0)
            # Simple on/off for now (full speed or off)
            # TODO: Implement software PWM for variable speed
            self.line_ena.set_value(1 if speed > 0 else 0)
            self.line_enb.set_value(1 if speed > 0 else 0)
            self._pwm_duty_a = speed
            self._pwm_duty_b = speed
        
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
        elif USE_GPIOD:
            # Backward: IN1=LOW, IN2=HIGH, IN3=LOW, IN4=HIGH
            self.line_in1.set_value(0)
            self.line_in2.set_value(1)
            self.line_in3.set_value(0)
            self.line_in4.set_value(1)
            self.line_ena.set_value(1 if speed > 0 else 0)
            self.line_enb.set_value(1 if speed > 0 else 0)
            self._pwm_duty_a = speed
            self._pwm_duty_b = speed
        
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
        elif USE_GPIOD:
            # Left motor backward/slow, right motor forward
            self.line_in1.set_value(0)
            self.line_in2.set_value(1)
            self.line_in3.set_value(1)
            self.line_in4.set_value(0)
            self.line_ena.set_value(0)  # Left motor off/slow
            self.line_enb.set_value(1 if speed > 0 else 0)  # Right motor on
            self._pwm_duty_a = speed // 2
            self._pwm_duty_b = speed
        
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
        elif USE_GPIOD:
            # Left motor forward, right motor backward/slow
            self.line_in1.set_value(1)
            self.line_in2.set_value(0)
            self.line_in3.set_value(0)
            self.line_in4.set_value(1)
            self.line_ena.set_value(1 if speed > 0 else 0)  # Left motor on
            self.line_enb.set_value(0)  # Right motor off/slow
            self._pwm_duty_a = speed
            self._pwm_duty_b = speed // 2
        
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
        elif USE_GPIOD:
            # Turn off all motor control lines
            self.line_in1.set_value(0)
            self.line_in2.set_value(0)
            self.line_in3.set_value(0)
            self.line_in4.set_value(0)
            self.line_ena.set_value(0)
            self.line_enb.set_value(0)
            self._pwm_duty_a = 0
            self._pwm_duty_b = 0
        
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
        elif USE_GPIOD and not self.dummy_mode:
            # Release all GPIO lines
            try:
                self.line_ena.release()
                self.line_in1.release()
                self.line_in2.release()
                self.line_enb.release()
                self.line_in3.release()
                self.line_in4.release()
            except:
                pass
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
