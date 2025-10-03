"""
YOLOv8 Human Detection Module
Handles video capture and human detection with bounding boxes
"""
import cv2
import numpy as np
from ultralytics import YOLO
import time


class HumanDetector:
    def __init__(self, model_name='yolov8n.pt', conf_threshold=0.5, camera_index=0, resolution=(640, 480)):
        """
        Initialize YOLOv8 human detector
        
        Args:
            model_name: YOLOv8 model to use (default: yolov8n.pt - nano, fastest)
            conf_threshold: Confidence threshold for detections (default: 0.5)
            camera_index: Camera device index (default: 0)
            resolution: Camera resolution as (width, height) tuple
        """
        print(f"Loading YOLOv8 model: {model_name}")
        self.model = YOLO(model_name)
        self.conf_threshold = conf_threshold
        self.camera_index = camera_index
        self.resolution = resolution
        
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not self.cap.isOpened():
            raise Exception(f"Failed to open camera at index {camera_index}")
        
        print(f"Camera initialized: {resolution[0]}x{resolution[1]}")
        
        # COCO dataset class ID for person is 0
        self.person_class_id = 0
        
    def detect_humans(self, frame):
        """
        Detect humans in a frame
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            tuple: (processed_frame, detection_count)
        """
        # Run YOLOv8 inference
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        # Count humans
        human_count = 0
        
        # Draw bounding boxes
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class ID
                class_id = int(box.cls[0])
                
                # Check if detection is a person
                if class_id == self.person_class_id:
                    human_count += 1
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    
                    # Get confidence
                    confidence = float(box.conf[0])
                    
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw label
                    label = f"Person {confidence:.2f}"
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                (x1 + label_size[0], y1), (0, 255, 0), -1)
                    cv2.putText(frame, label, (x1, y1 - 5), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame, human_count
    
    def add_info_overlay(self, frame, human_count, distance, fps=0):
        """
        Add information overlay to frame
        
        Args:
            frame: Input frame
            human_count: Number of detected humans
            distance: Distance from ultrasonic sensor (cm)
            fps: Frames per second
            
        Returns:
            Frame with overlay
        """
        height, width = frame.shape[:2]
        
        # Semi-transparent overlay background
        overlay = frame.copy()
        
        # Top-left: Human count
        count_text = f"Humans: {human_count}"
        cv2.rectangle(overlay, (10, 10), (200, 60), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        cv2.putText(frame, count_text, (20, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        # Top-right: Distance
        if distance > 0:
            distance_text = f"Distance: {distance:.1f} cm"
        else:
            distance_text = "Distance: -- cm"
        
        text_size, _ = cv2.getTextSize(distance_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        overlay = frame.copy()
        cv2.rectangle(overlay, (width - text_size[0] - 30, 10), 
                     (width - 10, 50), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        cv2.putText(frame, distance_text, (width - text_size[0] - 20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Bottom-left: FPS
        if fps > 0:
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(frame, fps_text, (20, height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def read_frame(self):
        """
        Read a frame from the camera
        
        Returns:
            tuple: (success, frame)
        """
        return self.cap.read()
    
    def release(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()
        print("Camera released")


# Test code
if __name__ == "__main__":
    print("Testing YOLOv8 Human Detection")
    print("Press 'q' to exit\n")
    
    detector = HumanDetector()
    
    try:
        fps_time = time.time()
        fps = 0
        
        while True:
            success, frame = detector.read_frame()
            if not success:
                print("Failed to read frame")
                break
            
            # Detect humans
            processed_frame, human_count = detector.detect_humans(frame)
            
            # Calculate FPS
            current_time = time.time()
            fps = 1 / (current_time - fps_time)
            fps_time = current_time
            
            # Add overlay (with dummy distance)
            processed_frame = detector.add_info_overlay(processed_frame, human_count, 50.0, fps)
            
            # Display
            cv2.imshow('Human Detection', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        detector.release()
        cv2.destroyAllWindows()
        print("Test complete")
