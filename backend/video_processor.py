import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable, List, Dict
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, face_detector):
        self.face_detector = face_detector
        self.camera = None
        self.is_running = False
        self.frame_thread = None
        self.current_frame = None
        self.current_detections = []
        self.frame_lock = threading.Lock()
        self.detection_callback = None
        
    def start_camera(self, camera_index: int = 0) -> bool:
        """Start camera capture"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                return False
                
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_running = True
            self.frame_thread = threading.Thread(target=self._capture_frames)
            self.frame_thread.daemon = True
            self.frame_thread.start()
            
            logger.info("Camera started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera capture"""
        try:
            self.is_running = False
            if self.frame_thread:
                self.frame_thread.join(timeout=2.0)
                
            if self.camera:
                self.camera.release()
                self.camera = None
                
            logger.info("Camera stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping camera: {e}")
    
    def _capture_frames(self):
        """Capture frames in a separate thread"""
        frame_count = 0
        detection_interval = 5  # Process every 5th frame for performance
        
        while self.is_running:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                detections = []
                
                # Process detection every N frames to improve performance
                if frame_count % detection_interval == 0:
                    detections = self.face_detector.detect_faces_and_masks(frame)
                    
                    # Add timestamps to detections
                    current_time = time.time()
                    for detection in detections:
                        detection['timestamp'] = current_time
                    
                    # Store current detections
                    with self.frame_lock:
                        self.current_detections = detections
                        
                    # Call detection callback if set
                    if self.detection_callback and detections:
                        self.detection_callback(detections)
                else:
                    # Use previous detections for consistent overlay
                    with self.frame_lock:
                        detections = self.current_detections.copy()
                
                # Draw detections on frame
                annotated_frame = self.face_detector.draw_detections(frame, detections)
                
                # Store current frame
                with self.frame_lock:
                    self.current_frame = annotated_frame
                
                frame_count += 1
                time.sleep(0.03)  # Limit to ~30 FPS
                
            except Exception as e:
                logger.error(f"Error in frame capture: {e}")
                time.sleep(0.1)
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the current frame with detections"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
    
    def get_current_detections(self) -> List[Dict]:
        """Get current detection results"""
        with self.frame_lock:
            return self.current_detections.copy()
    
    def set_detection_callback(self, callback: Callable):
        """Set callback function for new detections"""
        self.detection_callback = callback
    
    def generate_frame_stream(self):
        """Generate frames for streaming"""
        while self.is_running:
            frame = self.get_current_frame()
            if frame is not None:
                try:
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    if ret:
                        yield (b'--frame\r\n'
                              b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                except Exception as e:
                    logger.error(f"Error encoding frame: {e}")
            
            time.sleep(0.033)  # ~30 FPS
    
    def is_camera_running(self) -> bool:
        """Check if camera is currently running"""
        return self.is_running and self.camera is not None