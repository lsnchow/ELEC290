"""
YOLOv8 Human Detection Module (Optimized for Raspberry Pi)
Handles video capture and human detection with bounding boxes
"""
import time
import cv2
import numpy as np
from ultralytics import YOLO

import config


class HumanDetector:
    def __init__(self, model_name='yolov8n.pt', conf_threshold=0.4, camera_index=0, resolution=(320, 240)):
        """
        Initialize YOLOv8 human detector
        
        Args:
            model_name: YOLOv8 model to use (default: yolov8n.pt - nano, fastest)
            conf_threshold: Confidence threshold for detections (default: 0.4)
            camera_index: Camera device index (default: 0)
            resolution: Camera resolution as (width, height) tuple
        """
        print(f"Loading YOLOv8 model: {model_name}")
        self.model = YOLO(model_name)
        
        # Optimize for Raspberry Pi
        self.model.fuse()  # Fuse layers for faster inference
        
        self.conf_threshold = conf_threshold
        self.camera_index = camera_index
        self.resolution = resolution
        self.frame_count = 0
        self.last_human_count = 0
        self.last_results = None
        
        # Initialize camera - try to find working camera
        self.cap = None
        cameras_to_try = [camera_index, 0, 1, 2, '/dev/video0', '/dev/video1']
        
        for cam_id in cameras_to_try:
            try:
                print(f"Trying camera: {cam_id}")
                test_cap = cv2.VideoCapture(cam_id)
                if test_cap.isOpened():
                    # Test if we can actually read a frame
                    ret, _ = test_cap.read()
                    if ret:
                        self.cap = test_cap
                        self.camera_index = cam_id
                        print(f"✓ Successfully opened camera: {cam_id}")
                        break
                    else:
                        test_cap.release()
                else:
                    test_cap.release()
            except Exception as e:
                print(f"  Failed: {e}")
                continue
        
        if self.cap is None or not self.cap.isOpened():
            raise RuntimeError(
                "Could not find any working camera. Check:\n"
                "  1. Camera is connected (USB or ribbon cable)\n"
                "  2. Run 'ls /dev/video*' to see available cameras\n"
                "  3. Run 'v4l2-ctl --list-devices' for more info"
            )
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print(f"Camera initialized: {resolution[0]}x{resolution[1]}")
        print(f"✓ Model loaded (optimized for Pi)")
        print(f"  Image size: {config.IMGSZ}x{config.IMGSZ}")
        print(f"  Processing every {config.PROCESS_EVERY_N_FRAMES} frames")
        
        # COCO dataset class ID for person is 0
        self.person_class_id = 0
        
    def detect_humans(self, frame):
        """
        Detect humans in a frame (optimized with frame skipping)
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            tuple: (processed_frame, detection_count)
        """
        self.frame_count += 1
        
        # Skip frames for better performance
        if self.frame_count % config.PROCESS_EVERY_N_FRAMES != 0:
            # Use cached results if available
            if self.last_results is not None:
                return self._draw_cached_results(frame), self.last_human_count
            # Return frame without detection if no cached results
            return frame, 0
        
        # Run YOLOv8 inference with optimization
        try:
            results = self.model(
                frame, 
                conf=self.conf_threshold, 
                verbose=False,
                imgsz=config.IMGSZ,  # Smaller size = much faster
                iou=config.IOU_THRESHOLD,
                classes=[self.person_class_id],  # Only detect persons
                device='cpu',
                half=False  # Don't use FP16 on CPU
            )
        except Exception as e:
            print(f"YOLO inference error: {e}")
            return frame, 0
        
        # Store results for caching
        self.last_results = results
        
        # Count humans
        human_count = 0
        
        # Draw bounding boxes
        for result in results:
            boxes = result.boxes
            if boxes is not None:
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
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), (0, 255, 0), -1)
                        cv2.putText(frame, label, (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        self.last_human_count = human_count
        return frame, human_count
    
    def _draw_cached_results(self, frame):
        """Draw last detection results on a new frame"""
        if self.last_results is None:
            return frame
        
        for result in self.last_results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    if class_id == self.person_class_id:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        confidence = float(box.conf[0])
                        
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label = f"Person {confidence:.2f}"
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), (0, 255, 0), -1)
                        cv2.putText(frame, label, (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        return frame
    
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
