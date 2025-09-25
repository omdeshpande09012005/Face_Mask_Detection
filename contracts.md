# Face Mask Detection System - Backend Integration Contracts

## API Contracts

### 1. Video Stream Endpoint
**Endpoint:** `/api/video_feed`
**Method:** GET
**Response:** Multipart video stream (MJPEG)
**Description:** Real-time annotated video feed with detection overlays

### 2. Detection Statistics
**Endpoint:** `/api/statistics`
**Method:** GET
**Response:**
```json
{
  "totalDetections": 147,
  "maskedCount": 112,
  "unmaskedCount": 35,
  "complianceRate": 76.2,
  "avgConfidence": 0.92,
  "activeAlerts": 3,
  "lastUpdate": "2025-09-25T14:32:15Z"
}
```

### 3. Detection History
**Endpoint:** `/api/detections`
**Method:** GET
**Query Params:** `limit` (default: 50)
**Response:**
```json
{
  "detections": [
    {
      "id": "uuid",
      "timestamp": "2025-09-25T14:32:15Z",
      "hasMask": true,
      "confidence": 0.94,
      "bbox": {"x": 150, "y": 120, "w": 100, "h": 120},
      "alertTriggered": false
    }
  ]
}
```

### 4. Detection Controls
**Endpoint:** `/api/detection/start`
**Method:** POST
**Response:** `{"success": true, "message": "Detection started"}`

**Endpoint:** `/api/detection/stop`
**Method:** POST
**Response:** `{"success": true, "message": "Detection stopped"}`

### 5. Settings Management
**Endpoint:** `/api/settings`
**Method:** GET/PUT
**Payload:**
```json
{
  "visualAlerts": true,
  "soundAlerts": true,
  "confidenceThreshold": 0.8,
  "alertCooldown": 5000
}
```

### 6. WebSocket Events
**Endpoint:** `/api/ws`
**Events:**
- `detection_update`: Real-time detection results
- `statistics_update`: Updated compliance statistics
- `alert_triggered`: Mask violation alerts

## Data Models

### Detection Model
```python
class Detection(BaseModel):
    id: str
    timestamp: datetime
    hasMask: bool
    confidence: float
    bbox: Dict[str, int]  # x, y, w, h
    alertTriggered: bool
```

### Statistics Model
```python
class Statistics(BaseModel):
    totalDetections: int
    maskedCount: int
    unmaskedCount: int
    complianceRate: float
    avgConfidence: float
    activeAlerts: int
    lastUpdate: datetime
```

## Frontend Integration Points

### Mock Data Replacement
1. **Dashboard.jsx**: Replace mockDetectionData with API calls
2. **WebcamCapture.jsx**: Connect to `/api/video_feed`
3. **Real-time updates**: Implement WebSocket connections

### Frontend Changes Required
1. Add axios calls to replace mock functions
2. Implement WebSocket client for live updates
3. Connect video stream to backend endpoint
4. Handle loading states and error scenarios

## Backend Implementation Plan

### Phase 1: Core Detection Engine
- OpenCV webcam integration
- Haar Cascade face detection
- Pre-trained mask classification model
- Frame processing pipeline

### Phase 2: API Layer
- FastAPI endpoints
- Video streaming
- Database integration for logging
- WebSocket implementation

### Phase 3: Integration
- Connect frontend to backend APIs
- Real-time data synchronization
- Alert system integration
- Performance optimization

## Technical Dependencies
- OpenCV for computer vision
- TensorFlow/Keras for AI model
- WebSocket for real-time communication
- MongoDB for detection logging
- Pre-trained mask detection model