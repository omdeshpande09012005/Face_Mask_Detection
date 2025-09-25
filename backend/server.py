from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import os
import logging
import cv2
import numpy as np
from PIL import Image
import io
import json
from pathlib import Path
from dotenv import load_dotenv
import asyncio
import time

# Import our detection modules
from face_detection import FaceMaskDetector
from video_processor import VideoProcessor
from detection_manager import DetectionManager
from websocket_manager import WebSocketManager

# Setup
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Global variables
face_detector = None
video_processor = None
detection_manager = None
websocket_manager = None
db = None

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'face_mask_detection')]

# Pydantic models
class Detection(BaseModel):
    id: str
    timestamp: str
    hasMask: bool
    confidence: float
    bbox: Dict[str, int]
    alertTriggered: bool = False

class Statistics(BaseModel):
    totalDetections: int
    maskedCount: int
    unmaskedCount: int
    complianceRate: float
    avgConfidence: float
    activeAlerts: int
    lastUpdate: str

class Settings(BaseModel):
    visualAlerts: bool = True
    soundAlerts: bool = True
    confidenceThreshold: float = 0.8
    alertCooldown: int = 5000

class DetectionResponse(BaseModel):
    success: bool
    detections: List[Detection]
    statistics: Statistics

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global face_detector, video_processor, detection_manager, websocket_manager
    
    # Startup
    logging.info("Initializing Face Mask Detection System...")
    
    try:
        # Initialize face detector
        face_detector = FaceMaskDetector()
        logging.info("Face detector initialized")
        
        # Initialize detection manager
        detection_manager = DetectionManager(db)
        logging.info("Detection manager initialized")
        
        # Initialize video processor
        video_processor = VideoProcessor(face_detector)
        logging.info("Video processor initialized")
        
        # Initialize WebSocket manager
        websocket_manager = WebSocketManager()
        logging.info("WebSocket manager initialized")
        
        # Set up detection callback
        def on_new_detections(detections):
            asyncio.create_task(handle_new_detections(detections))
        
        video_processor.set_detection_callback(on_new_detections)
        
        logging.info("Face Mask Detection System initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize system: {e}")
        raise
    
    yield
    
    # Shutdown
    logging.info("Shutting down Face Mask Detection System...")
    if video_processor:
        video_processor.stop_camera()
    if client:
        client.close()

async def handle_new_detections(detections):
    """Handle new detections from video processor"""
    try:
        if detection_manager and websocket_manager:
            # Process detections
            processed_detections = await detection_manager.process_detections(detections)
            
            # Send updates via WebSocket
            await websocket_manager.send_detection_update(processed_detections)
            
            # Send statistics update
            stats = detection_manager.get_statistics()
            await websocket_manager.send_statistics_update(stats)
            
            # Send alerts for mask violations
            for detection in processed_detections:
                if detection['alertTriggered']:
                    await websocket_manager.send_alert({
                        'message': f"Mask violation detected with {detection['confidence']:.2f} confidence",
                        'detection': detection
                    })
    except Exception as e:
        logging.error(f"Error handling new detections: {e}")

# Create the main app
app = FastAPI(
    title="Face Mask Detection API",
    description="Real-time face mask detection system with OpenCV and TensorFlow",
    version="1.0.0",
    lifespan=lifespan
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Face Mask Detection System API", "status": "running"}

@api_router.post("/detection/start")
async def start_detection():
    """Start face mask detection"""
    try:
        if video_processor and not video_processor.is_camera_running():
            success = video_processor.start_camera()
            if success:
                return {"success": True, "message": "Detection started successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to start camera")
        else:
            return {"success": True, "message": "Detection already running"}
    except Exception as e:
        logger.error(f"Error starting detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/detection/stop")
async def stop_detection():
    """Stop face mask detection"""
    try:
        if video_processor and video_processor.is_camera_running():
            video_processor.stop_camera()
            return {"success": True, "message": "Detection stopped successfully"}
        else:
            return {"success": True, "message": "Detection not running"}
    except Exception as e:
        logger.error(f"Error stopping detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/video_feed")
async def video_feed():
    """Stream video feed with face mask detection"""
    try:
        if not video_processor or not video_processor.is_camera_running():
            raise HTTPException(status_code=404, detail="Camera not running")
        
        return StreamingResponse(
            video_processor.generate_frame_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except Exception as e:
        logger.error(f"Error in video feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/statistics", response_model=Statistics)
async def get_statistics():
    """Get detection statistics"""
    try:
        if detection_manager:
            return detection_manager.get_statistics()
        else:
            return Statistics(
                totalDetections=0,
                maskedCount=0,
                unmaskedCount=0,
                complianceRate=0.0,
                avgConfidence=0.0,
                activeAlerts=0,
                lastUpdate=datetime.utcnow().isoformat()
            )
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/detections")
async def get_detections(limit: int = 50):
    """Get detection history"""
    try:
        if detection_manager:
            detections = detection_manager.get_detection_history(limit)
            return {"detections": detections}
        else:
            return {"detections": []}
    except Exception as e:
        logger.error(f"Error getting detections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/settings", response_model=Settings)
async def get_settings():
    """Get current settings"""
    try:
        if detection_manager:
            return detection_manager.get_settings()
        else:
            return Settings()
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/settings", response_model=Settings)
async def update_settings(settings: Settings):
    """Update detection settings"""
    try:
        if detection_manager:
            updated_settings = detection_manager.update_settings(settings.dict())
            return updated_settings
        else:
            return Settings()
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/detect_image")
async def detect_image(file: UploadFile = File(...)):
    """Detect faces and masks in uploaded image"""
    try:
        # Read image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Detect faces and masks
        detections = face_detector.detect_faces_and_masks(image)
        
        # Add timestamps
        for detection in detections:
            detection['timestamp'] = datetime.utcnow().isoformat()
        
        # Process detections if manager is available
        if detection_manager:
            processed_detections = await detection_manager.process_detections(detections)
            statistics = detection_manager.get_statistics()
        else:
            processed_detections = detections
            statistics = Statistics(
                totalDetections=len(detections),
                maskedCount=sum(1 for d in detections if d['hasMask']),
                unmaskedCount=sum(1 for d in detections if not d['hasMask']),
                complianceRate=0.0,
                avgConfidence=0.0,
                activeAlerts=0,
                lastUpdate=datetime.utcnow().isoformat()
            )
        
        return DetectionResponse(
            success=True,
            detections=processed_detections,
            statistics=statistics
        )
        
    except Exception as e:
        logger.error(f"Error detecting image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    
    if websocket_manager:
        await websocket_manager.connect(websocket)
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get('type') == 'ping':
                    await websocket.send_text(json.dumps({'type': 'pong'}))
                
        except WebSocketDisconnect:
            await websocket_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket_manager.disconnect(websocket)

# Include the router in the main app
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()