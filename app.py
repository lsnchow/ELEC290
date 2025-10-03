"""
Flask MJPEG Streaming Server with YOLOv8 Human Detection and Ultrasonic Sensor
"""
from flask import Flask, render_template, Response
import cv2
import time
from detector import HumanDetector
from ultrasonic import UltrasonicSensor
import config

app = Flask(__name__)

# Global objects
detector = None
sensor = None


def initialize_system():
    """Initialize detection and sensor systems"""
    global detector, sensor
    
    print("Initializing system...")
    
    # Initialize human detector
    detector = HumanDetector(
        model_name=config.YOLO_MODEL,
        conf_threshold=config.CONFIDENCE_THRESHOLD,
        camera_index=config.CAMERA_INDEX,
        resolution=(config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
    )
    
    # Initialize ultrasonic sensor
    sensor = UltrasonicSensor(
        trig_pin=config.TRIG_PIN,
        echo_pin=config.ECHO_PIN
    )
    
    # Start continuous distance reading
    sensor.start_continuous_reading(interval=config.DISTANCE_READ_INTERVAL)
    
    print("System initialized successfully!")


def generate_frames():
    """
    Generator function for MJPEG streaming
    Yields frames with detection and distance overlay
    """
    global detector, sensor
    
    frame_time = time.time()
    fps = 0
    
    while True:
        try:
            # Read frame from camera
            success, frame = detector.read_frame()
            if not success:
                print("Failed to read frame from camera")
                break
            
            # Detect humans
            processed_frame, human_count = detector.detect_humans(frame)
            
            # Get distance from sensor
            distance = sensor.get_distance()
            
            # Calculate FPS
            current_time = time.time()
            fps = 1 / (current_time - frame_time) if (current_time - frame_time) > 0 else 0
            frame_time = current_time
            
            # Add information overlay
            processed_frame = detector.add_info_overlay(
                processed_frame, 
                human_count, 
                distance, 
                fps
            )
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame, 
                                      [cv2.IMWRITE_JPEG_QUALITY, config.JPEG_QUALITY])
            
            if not ret:
                continue
            
            # Convert to bytes
            frame_bytes = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Limit FPS for streaming
            time.sleep(1 / config.STREAM_FPS_LIMIT)
            
        except Exception as e:
            print(f"Error in frame generation: {e}")
            break


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Returns MJPEG stream"""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/status')
def status():
    """Return system status as JSON"""
    global sensor
    
    return {
        'status': 'running',
        'distance': sensor.get_distance() if sensor else -1,
        'camera_resolution': f"{config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}",
        'model': config.YOLO_MODEL
    }


def cleanup():
    """Clean up resources on shutdown"""
    global detector, sensor
    
    print("\nShutting down...")
    
    if sensor:
        sensor.cleanup()
    
    if detector:
        detector.release()
    
    print("Cleanup complete")


if __name__ == '__main__':
    try:
        initialize_system()
        
        print(f"\n{'='*50}")
        print(f"Server starting on http://{config.HOST}:{config.PORT}")
        print(f"Access from your Mac: http://<raspberry-pi-ip>:{config.PORT}")
        print(f"To find Pi IP, run: hostname -I")
        print(f"{'='*50}\n")
        
        # Run Flask app
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        cleanup()
