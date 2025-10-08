"""
Configuration settings for autonomous tracking robot car
"""

# Camera settings
CAMERA_INDEX = 0  # 0 for /dev/video0
CAMERA_WIDTH = 320  # Optimized for Pi
CAMERA_HEIGHT = 240
CAMERA_FPS = 15

# YOLO settings
YOLO_MODEL = 'yolov8n.pt'
CONFIDENCE_THRESHOLD = 0.35
IOU_THRESHOLD = 0.5
TARGET_CLASS = 0  # person

# Performance optimization
IMGSZ = 256
PROCESS_EVERY_N_FRAMES = 3

# Motor control pins (L298N) - BCM numbering
ENA = 17  # Motor A PWM (Physical Pin 11)
IN1 = 27  # Motor A Direction 1 (Physical Pin 13)
IN2 = 22  # Motor A Direction 2 (Physical Pin 15)
ENB = 18  # Motor B PWM (Physical Pin 12)
IN3 = 23  # Motor B Direction 1 (Physical Pin 16)
IN4 = 24  # Motor B Direction 2 (Physical Pin 18)

# Motor settings
DEFAULT_SPEED = 60  # Default motor speed (0-100)
TURN_SPEED = 50  # Speed when turning
MIN_SPEED = 30  # Minimum speed to overcome friction

# Arduino serial settings
ARDUINO_PORT = '/dev/ttyUSB0'  # Try /dev/ttyACM0 if this doesn't work
ARDUINO_BAUD = 9600
ARDUINO_DEBUG = True  # Set to True for detailed Arduino debugging

# Auto-tracking settings
TRACKING_ENABLED = True
STOP_DISTANCE = 8  # Stop if Arduino distance < 8cm
FOLLOW_DISTANCE = 50  # Ideal following distance (cm)
PERSON_LOST_TIMEOUT = 3  # Stop if person not detected for 3 seconds
CENTER_TOLERANCE = 50  # Pixel tolerance for "centered" detection

# Flask server settings
HOST = '0.0.0.0'
PORT = 5000
DEBUG = False

# Streaming settings
JPEG_QUALITY = 60
STREAM_FPS_LIMIT = 12

# Control mode
DEFAULT_MODE = 'manual'  # 'manual' or 'auto'
