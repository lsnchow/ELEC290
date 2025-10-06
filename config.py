"""
Configuration settings for the detection system (Optimized for Raspberry Pi)
"""

# Camera settings
CAMERA_INDEX = 0  # 0 for /dev/video0, adjust if using different camera
CAMERA_WIDTH = 320  # Reduced from 640 for much faster processing
CAMERA_HEIGHT = 240  # Reduced from 480
CAMERA_FPS = 15  # Lower FPS for smoother performance

# YOLO settings
YOLO_MODEL = 'yolov8n.pt'  # yolov8n.pt (nano - fastest)
CONFIDENCE_THRESHOLD = 0.35  # Detection confidence (lower = more detections but less accurate)
IOU_THRESHOLD = 0.5
TARGET_CLASS = 0  # 0 = person in COCO dataset

# Performance optimization (ULTRA FAST MODE)
IMGSZ = 256  # Even smaller inference size (256 instead of 320) = MUCH faster!
PROCESS_EVERY_N_FRAMES = 3  # Process every 3rd frame (skip 2) for maximum speed

# Ultrasonic sensor GPIO pins (BCM numbering)
TRIG_PIN = 23  # GPIO 23 (Physical Pin 16)
ECHO_PIN = 24  # GPIO 24 (Physical Pin 18)
DISTANCE_READ_INTERVAL = 0.2  # Seconds between distance measurements

# Flask server settings
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5000
DEBUG = False  # Set to False for production

# Performance settings
JPEG_QUALITY = 60  # JPEG compression quality (1-100), lower = faster
STREAM_FPS_LIMIT = 12  # Max FPS for MJPEG stream to reduce bandwidth
