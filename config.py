"""
Configuration settings for the detection system
"""

# Camera settings
CAMERA_INDEX = 0  # 0 for /dev/video0, adjust if using different camera
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# YOLO settings
YOLO_MODEL = 'yolov8n.pt'  # yolov8n.pt (nano - fastest), yolov8s.pt, yolov8m.pt
CONFIDENCE_THRESHOLD = 0.5  # Detection confidence (0.0 to 1.0)

# Ultrasonic sensor GPIO pins (BCM numbering)
TRIG_PIN = 23  # GPIO 23 (Physical Pin 16)
ECHO_PIN = 24  # GPIO 24 (Physical Pin 18)
DISTANCE_READ_INTERVAL = 0.1  # Seconds between distance measurements

# Flask server settings
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5000
DEBUG = False  # Set to False for production

# Performance settings
JPEG_QUALITY = 80  # JPEG compression quality (1-100)
STREAM_FPS_LIMIT = 15  # Max FPS for MJPEG stream to reduce bandwidth
