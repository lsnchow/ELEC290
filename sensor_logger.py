"""
Sensor Data Logger
Logs temperature and sensor data with timestamps for Excel export
"""
import time
from datetime import datetime
from collections import deque
import threading


class SensorLogger:
    def __init__(self, max_entries=1000):
        """
        Initialize sensor logger
        
        Args:
            max_entries: Maximum number of entries to keep in memory (default: 1000)
        """
        self.max_entries = max_entries
        self.data_log = deque(maxlen=max_entries)
        self.lock = threading.Lock()
        self.logging_enabled = True
        
    def log_data(self, arduino_data):
        """
        Log sensor data with timestamp
        
        Args:
            arduino_data: Dictionary containing sensor readings
        """
        if not self.logging_enabled:
            return
            
        timestamp = datetime.now()
        
        with self.lock:
            entry = {
                'timestamp': timestamp,
                'datetime_str': timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],  # Include milliseconds
                'temperature': arduino_data.get('temperature', 0),
                'distance': arduino_data.get('distance', 0),
                'accel_x': arduino_data.get('accel_x', 0),
                'accel_y': arduino_data.get('accel_y', 0),
                'accel_z': arduino_data.get('accel_z', 0),
                'gyro_x': arduino_data.get('gyro_x', 0),
                'gyro_y': arduino_data.get('gyro_y', 0),
                'gyro_z': arduino_data.get('gyro_z', 0),
            }
            self.data_log.append(entry)
    
    def get_csv_data(self):
        """
        Get logged data as CSV string
        
        Returns:
            CSV formatted string with header and data rows
        """
        with self.lock:
            if len(self.data_log) == 0:
                return "No data logged yet"
            
            # CSV header
            csv_lines = [
                "Timestamp,Temperature (°C),Distance (cm),Accel X (m/s²),Accel Y (m/s²),Accel Z (m/s²),Gyro X (°/s),Gyro Y (°/s),Gyro Z (°/s)"
            ]
            
            # Data rows
            for entry in self.data_log:
                row = (
                    f"{entry['datetime_str']},"
                    f"{entry['temperature']:.2f},"
                    f"{entry['distance']:.2f},"
                    f"{entry['accel_x']:.2f},"
                    f"{entry['accel_y']:.2f},"
                    f"{entry['accel_z']:.2f},"
                    f"{entry['gyro_x']:.2f},"
                    f"{entry['gyro_y']:.2f},"
                    f"{entry['gyro_z']:.2f}"
                )
                csv_lines.append(row)
            
            return '\n'.join(csv_lines)
    
    def get_stats(self):
        """
        Get statistics about logged data
        
        Returns:
            Dictionary with stats (count, time range, etc.)
        """
        with self.lock:
            if len(self.data_log) == 0:
                return {
                    'count': 0,
                    'start_time': None,
                    'end_time': None,
                    'duration': 0
                }
            
            first_entry = self.data_log[0]
            last_entry = self.data_log[-1]
            duration = (last_entry['timestamp'] - first_entry['timestamp']).total_seconds()
            
            return {
                'count': len(self.data_log),
                'start_time': first_entry['datetime_str'],
                'end_time': last_entry['datetime_str'],
                'duration': duration,
                'temp_avg': sum(e['temperature'] for e in self.data_log) / len(self.data_log),
                'temp_min': min(e['temperature'] for e in self.data_log),
                'temp_max': max(e['temperature'] for e in self.data_log),
            }
    
    def clear_log(self):
        """Clear all logged data"""
        with self.lock:
            self.data_log.clear()
    
    def enable_logging(self):
        """Enable data logging"""
        self.logging_enabled = True
    
    def disable_logging(self):
        """Disable data logging"""
        self.logging_enabled = False
