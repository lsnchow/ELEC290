"""
Auto-Tracking Module
Implements autonomous person-following behavior
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
        
        print("✓ Person tracker initialized")
    
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
        Process YOLO detections and control motors
        
        Args:
            detections: List of [x1, y1, x2, y2, confidence]
            human_count: Number of humans detected
            
        Returns:
            dict: Tracking status
        """
        if not self.enabled:
            return {"status": "disabled"}
        
        # Get distance from Arduino
        arduino_data = self.arduino.get_data()
        distance = arduino_data.get('distance', 999)
        
        # Safety: Stop if too close
        if distance < config.STOP_DISTANCE:
            self.motors.stop()
            return {
                "status": "stopped",
                "reason": "too_close",
                "distance": distance
            }
        
        # Check if person detected
        if human_count == 0:
            # Person lost - check timeout
            if time.time() - self.last_detection_time > config.PERSON_LOST_TIMEOUT:
                self.motors.stop()
                return {
                    "status": "stopped",
                    "reason": "person_lost"
                }
            else:
                # Keep last command for a bit
                return {
                    "status": "searching",
                    "reason": "temporary_loss"
                }
        
        # Person detected - update time
        self.last_detection_time = time.time()
        
        # Find largest (closest) detection
        largest_detection = max(detections, key=lambda d: (d[2] - d[0]) * (d[3] - d[1]))
        x1, y1, x2, y2, conf = largest_detection
        
        # Calculate center of bounding box
        person_center_x = (x1 + x2) // 2
        person_width = x2 - x1
        
        # Calculate offset from center
        offset = person_center_x - self.frame_center_x
        
        # Determine action based on offset and person size
        action = self._calculate_action(offset, person_width, distance)
        
        return {
            "status": "tracking",
            "action": action,
            "offset": offset,
            "person_center": person_center_x,
            "distance": distance
        }
    
    def _calculate_action(self, offset, person_width, distance):
        """
        Calculate motor action based on person position
        
        Args:
            offset: Horizontal offset from center (negative = left, positive = right)
            person_width: Width of person bounding box
            distance: Distance from Arduino sensor
            
        Returns:
            str: Action taken
        """
        # Person centered?
        if abs(offset) < config.CENTER_TOLERANCE:
            # Check distance
            if distance > config.FOLLOW_DISTANCE + 20:
                # Too far - move forward
                self.motors.forward(config.DEFAULT_SPEED)
                return "forward"
            elif distance < config.FOLLOW_DISTANCE - 10:
                # Too close - move backward
                self.motors.backward(config.DEFAULT_SPEED)
                return "backward"
            else:
                # Good distance - stop
                self.motors.stop()
                return "stopped_good_distance"
        
        # Person not centered - turn towards them
        if offset < -config.CENTER_TOLERANCE:
            # Person on left - turn left
            self.motors.left(config.TURN_SPEED)
            return "turning_left"
        else:
            # Person on right - turn right
            self.motors.right(config.TURN_SPEED)
            return "turning_right"
    
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
