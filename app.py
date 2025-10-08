"""
Autonomous Tracking Robot Car - Flask Server with WebSocket Control
"""
from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO, emit
import cv2
import time
import config
from detector import HumanDetector
from motors import MotorController
from arduino_serial import ArduinoSerial
from tracking import PersonTracker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'batman-secret-key-290'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global objects
detector = None
motors = None
arduino = None
tracker = None
control_mode = config.DEFAULT_MODE  # 'manual' or 'auto'


def initialize_system():
    """Initialize all systems"""
    global detector, motors, arduino, tracker
    
    print("Initializing autonomous tracking robot...")
    
    # Initialize human detector
    detector = HumanDetector(
        model_name=config.YOLO_MODEL,
        conf_threshold=config.CONFIDENCE_THRESHOLD,
        camera_index=config.CAMERA_INDEX,
        resolution=(config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
    )
    
    # Initialize motor controller
    motors = MotorController(
        ena=config.ENA, in1=config.IN1, in2=config.IN2,
        enb=config.ENB, in3=config.IN3, in4=config.IN4
    )
    
    # Initialize Arduino serial
    arduino = ArduinoSerial(
        port=config.ARDUINO_PORT,
        baudrate=config.ARDUINO_BAUD,
        debug=config.ARDUINO_DEBUG
    )
    arduino.start()
    
    # Initialize person tracker
    tracker = PersonTracker(motors, arduino)
    if config.TRACKING_ENABLED and control_mode == 'auto':
        tracker.enable()
    
    print("System initialized successfully!")


def generate_frames():
    """
    Generator function for MJPEG streaming
    Yields frames with detection and overlays
    """
    global detector, arduino, tracker, control_mode
    
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
            
            # Get Arduino sensor data
            arduino_data = arduino.get_data()
            distance = arduino_data['distance']
            
            # Auto-tracking if enabled
            if control_mode == 'auto' and tracker.enabled:
                # Get detections for tracking
                detections = detector.last_results[0].boxes.xyxy.cpu().numpy().tolist() if detector.last_results and len(detector.last_results) > 0 and detector.last_results[0].boxes is not None else []
                tracking_status = tracker.process_detection(detections, human_count)
            
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
            
            # Add mode indicator
            mode_text = f"Mode: {control_mode.upper()}"
            cv2.putText(processed_frame, mode_text, (10, processed_frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
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
    global arduino, motors, tracker, control_mode
    
    arduino_data = arduino.get_data() if arduino else {}
    motor_status = motors.get_status() if motors else {}
    
    return jsonify({
        'status': 'running',
        'mode': control_mode,
        'camera_resolution': f"{config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}",
        'model': config.YOLO_MODEL,
        'sensors': arduino_data,
        'motors': motor_status,
        'tracking_enabled': tracker.enabled if tracker else False
    })

@app.route('/sensor_data')
def sensor_data():
    """Stream sensor data as JSON"""
    global arduino
    
    if arduino:
        return jsonify(arduino.get_data())
    return jsonify({'error': 'Arduino not connected'})

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print('Client connected')
    emit('status', {'mode': control_mode, 'connected': True})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('Client disconnected')
    if control_mode == 'manual':
        motors.stop()

@socketio.on('set_mode')
def handle_set_mode(data):
    """Switch between auto/manual mode"""
    global control_mode, tracker
    
    mode = data.get('mode', 'manual')
    if mode in ['auto', 'manual']:
        control_mode = mode
        print(f"Mode switched to: {mode}")
        
        if mode == 'auto':
            tracker.enable()
        else:
            tracker.disable()
            motors.stop()
        
        emit('mode_changed', {'mode': mode}, broadcast=True)

@socketio.on('manual_control')
def handle_manual_control(data):
    """Handle manual WASD control"""
    global control_mode, motors
    
    if control_mode != 'manual':
        return
    
    command = data.get('command', 'stop')
    speed = data.get('speed', config.DEFAULT_SPEED)
    
    if command == 'forward' or command == 'w':
        motors.forward(speed)
    elif command == 'backward' or command == 's':
        motors.backward(speed)
    elif command == 'left' or command == 'a':
        motors.left(speed)
    elif command == 'right' or command == 'd':
        motors.right(speed)
    elif command == 'stop':
        motors.stop()
    
    emit('motor_status', motors.get_status(), broadcast=True)

@socketio.on('emergency_stop')
def handle_emergency_stop():
    """Emergency stop - stops motors and switches to manual"""
    global control_mode, motors, tracker
    
    motors.stop()
    control_mode = 'manual'
    tracker.disable()
    
    print("EMERGENCY STOP activated")
    emit('mode_changed', {'mode': 'manual', 'emergency': True}, broadcast=True)


def cleanup():
    """Clean up resources on shutdown"""
    global detector, motors, arduino, tracker
    
    print("\nShutting down...")
    
    if tracker:
        tracker.disable()
    
    if motors:
        motors.cleanup()
    
    if arduino:
        arduino.stop()
    
    if detector:
        detector.release()
    
    print("Cleanup complete")


if __name__ == '__main__':
    try:
        initialize_system()
        
        print(f"\n{'='*70}")
        print(f"AUTONOMOUS TRACKING ROBOT - ONLINE")
        print(f"{'='*70}")
        print(f"Server: http://{config.HOST}:{config.PORT}")
        print(f"Access from your Mac: http://<raspberry-pi-ip>:{config.PORT}")
        print(f"Mode: {control_mode.upper()}")
        print(f"{'='*70}\n")
        
        # Run Flask app with SocketIO
        socketio.run(
            app,
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup()
