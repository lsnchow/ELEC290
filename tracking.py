"""
Auto-Tracking Module
Implements autonomous person-following behavior with ultrasonic safety stop
"""
import time
import config


class PersonTracker:
    def __init__(self, motor_controller, arduino_serial):
        """
        Initialize person tracker
        
        Args:
            motor_controller: MotorController instance
            arduino_serial: ArduinoSerial instance
        """
        self.motors = motor_controller
        self.arduino = arduino_serial
        self.enabled = False
        self.last_detection_time = 0
        self.frame_center_x = config.CAMERA_WIDTH // 2
        self.frame_count = 0
        self.target_locked = False
        self.last_target = None
        
        # Safety settings
        self.EMERGENCY_STOP_DISTANCE = 20  # cm - stop if closer than this
        self.TARGET_RESELECT_FRAMES = 5  # Reselect target every 5 frames
        
        print("✓ Person tracker initialized")
        print(f"  Emergency stop: < {self.EMERGENCY_STOP_DISTANCE}cm")
        print(f"  Target reselect: every {self.TARGET_RESELECT_FRAMES} frames")
    
    def enable(self):
        """Enable auto-tracking mode"""
        self.enabled = True
        self.last_detection_time = time.time()
        print("Auto-tracking: ENABLED")
    
    def disable(self):
        """Disable auto-tracking and stop motors"""
        self.enabled = False
        self.motors.stop()
        print("Auto-tracking: DISABLED")
    
    def process_detection(self, detections, human_count):
        """
        Process YOLO detections and control motors with safety checks
        
        Args:
            detections: List of [x1, y1, x2, y2] bounding boxes
            human_count: Number of humans detected
            
        Returns:
            dict: Tracking status
        """
        if not self.enabled:
            return {"status": "disabled"}
        
        self.frame_count += 1
        
        # Get distance from ultrasonic sensor
        arduino_data = self.arduino.get_data()
        distance = arduino_data.get('distance', 999)
        
        # EMERGENCY STOP: Ultrasonic < 20cm
        if distance < self.EMERGENCY_STOP_DISTANCE and distance > 0:
            self.motors.stop()
            print(f"⚠️  EMERGENCY STOP: Obstacle at {distance:.1f}cm (< {self.EMERGENCY_STOP_DISTANCE}cm)")
            return {
                "status": "EMERGENCY_STOP",
                "reason": "obstacle_too_close",
                "distance": distance,
                "threshold": self.EMERGENCY_STOP_DISTANCE
            }
        
        # No person detected
        if human_count == 0 or len(detections) == 0:
            # Person lost - stop after timeout
            if time.time() - self.last_detection_time > 2.0:  # 2 second timeout
                self.motors.stop()
                self.target_locked = False
                return {
                    "status": "stopped",
                    "reason": "no_person_detected"
                }
            else:
                # Keep searching
                return {
                    "status": "searching",
                    "reason": "temporary_loss"
                }
        
        # Person detected - update time
        self.last_detection_time = time.time()
        
        # Reselect target every N frames (or if no target locked)
        if not self.target_locked or self.frame_count % self.TARGET_RESELECT_FRAMES == 0:
            # Find person with LARGEST bounding box (closest/most prominent)
            largest_detection = max(detections, key=lambda d: (d[2] - d[0]) * (d[3] - d[1]))
            self.last_target = largest_detection
            self.target_locked = True
        else:
            # Use previously locked target
            largest_detection = self.last_target if self.last_target else detections[0]
        
        x1, y1, x2, y2 = largest_detection[:4]
        
        # Calculate center of person's bounding box
        person_center_x = (x1 + x2) / 2
        person_width = x2 - x1
        
        # Calculate horizontal offset from frame center
        offset = person_center_x - self.frame_center_x
        
        # Determine action and control motors
        action = self._calculate_action(offset, person_width, distance)
        
        return {
            "status": "tracking",
            "action": action,
            "offset": offset,
            "person_center": person_center_x,
            "distance": distance,
            "target_locked": self.target_locked
        }
    
    def _calculate_action(self, offset, person_width, distance):
        """
        Calculate motor action based on person position
        Simple bang-bang control: center on person, then move forward
        
        Args:
            offset: Horizontal offset from center (negative = left, positive = right)
            person_width: Width of person bounding box
            distance: Distance from ultrasonic sensor
            
        Returns:
            str: Action description
        """
        # Define center tolerance (pixels)
        CENTER_THRESHOLD = 40  # Person is "centered" if within 40px of center
        
        # Priority 1: Center on person
        if abs(offset) > CENTER_THRESHOLD:
            if offset < 0:
                # Person on LEFT side - turn left
                self.motors.left(55)
                return "turn_left"
            else:
                # Person on RIGHT side - turn right
                self.motors.right(55)
                return "turn_right"
        
        # Priority 2: Person centered - move forward towards them
        # (Safety stop handled above if distance < 20cm)
        self.motors.forward(50)
        return "forward"
    
    def get_status(self):
        """Get current tracking status"""
        return {
            "enabled": self.enabled,
            "last_detection": time.time() - self.last_detection_time if self.last_detection_time > 0 else None
        }


# Test code
if __name__ == "__main__":
    print("Person Tracker Test")
    print("This module requires motor and arduino instances")
    print("Run from main app.py for full testing")
