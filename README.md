# 🎭 Face Mask Detection System

A real-time AI-powered face mask detection system built with React, FastAPI, OpenCV, and TensorFlow. This system provides live webcam monitoring, compliance tracking, and professional dashboard analytics for mask-wearing detection in public spaces, corporate environments, and healthcare facilities.

![Face Mask Detection Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![React](https://img.shields.io/badge/React-19.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.1-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.12.0-orange)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.20.0-orange)

## 🚀 Features

### 🎯 Core Functionality
- **Real-time Face Detection**: Uses OpenCV Haar Cascade for efficient face detection
- **AI-Powered Mask Classification**: CNN-based model for accurate mask/no-mask detection
- **Live Video Stream**: Real-time webcam processing with detection overlays
- **Confidence Scoring**: Provides confidence percentages for each detection
- **Alert System**: Visual and audio alerts for mask violations

### 📊 Analytics Dashboard
- **Compliance Tracking**: Real-time compliance rate monitoring
- **Detection Statistics**: Total detections, masked vs unmasked counts
- **Historical Data**: Detection history with timestamps and confidence scores
- **Progress Visualization**: Interactive progress bars and statistics cards
- **Export Functionality**: Data export for compliance reporting

### 🎨 User Interface
- **Professional Dark Theme**: Modern, responsive dashboard design
- **Real-time Updates**: WebSocket-powered live data streaming
- **Interactive Controls**: Settings panel for alerts and thresholds
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices
- **Accessibility**: WCAG-compliant design with proper contrast ratios

## 🛠️ Tech Stack

### Frontend
- **React 19.0** - Modern UI framework
- **TailwindCSS** - Utility-first CSS framework
- **Shadcn/ui** - Professional component library
- **Axios** - HTTP client for API communication
- **WebSocket** - Real-time communication

### Backend
- **FastAPI** - High-performance Python web framework
- **OpenCV** - Computer vision and image processing
- **TensorFlow/Keras** - Deep learning framework
- **MongoDB** - NoSQL database for data persistence
- **WebSocket** - Real-time bidirectional communication
- **Motor** - Async MongoDB driver

### AI/ML
- **Haar Cascade Classifier** - Face detection algorithm
- **Convolutional Neural Network** - Mask classification model
- **Image Preprocessing** - Real-time image processing pipeline
- **Confidence Scoring** - Prediction reliability metrics

## 📦 Installation

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **MongoDB**
- **Webcam/Camera** (for live detection)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/face-mask-detection-system.git
cd face-mask-detection-system
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your MongoDB connection string
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
yarn install

# Set environment variables
cp .env.example .env
# Edit .env with your backend URL
```

### 4. Database Setup
```bash
# Start MongoDB (if not running)
mongod --dbpath /path/to/your/db

# The application will automatically create necessary collections
```

## 🚀 Usage

### Development Mode

1. **Start Backend Server**:
```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

2. **Start Frontend Development Server**:
```bash
cd frontend
yarn start
```

3. **Access the Application**:
   - Open http://localhost:3000 in your browser
   - Click "Start Detection" to begin face mask monitoring

### Production Deployment

#### Using Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individual services
docker build -t face-mask-backend ./backend
docker build -t face-mask-frontend ./frontend

docker run -p 8001:8001 face-mask-backend
docker run -p 3000:3000 face-mask-frontend
```

#### Using Kubernetes
```bash
# Apply Kubernetes configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
```

## 📖 API Documentation

### Detection Endpoints

#### Start Detection
```http
POST /api/detection/start
```
**Response:**
```json
{
  "success": true,
  "message": "Detection started successfully"
}
```

#### Stop Detection
```http
POST /api/detection/stop
```

#### Get Statistics
```http
GET /api/statistics
```
**Response:**
```json
{
  "totalDetections": 147,
  "maskedCount": 112,
  "unmaskedCount": 35,
  "complianceRate": 76.2,
  "avgConfidence": 0.92,
  "activeAlerts": 3,
  "lastUpdate": "2024-01-15T10:30:00Z"
}
```

### Data Endpoints

#### Get Detection History
```http
GET /api/detections?limit=50
```

#### Upload Image for Detection
```http
POST /api/detect_image
Content-Type: multipart/form-data

{
  "file": [image_file]
}
```

### Settings Endpoints

#### Update Settings
```http
PUT /api/settings
Content-Type: application/json

{
  "visualAlerts": true,
  "soundAlerts": true,
  "confidenceThreshold": 0.8,
  "alertCooldown": 5000
}
```

### WebSocket Events

#### Connect to WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8001/api/ws');

// Event types:
// - detection_update: New detection results
// - statistics_update: Updated compliance stats
// - alert_triggered: Mask violation alerts
```

## 📁 Project Structure

```
face-mask-detection-system/
├── backend/
│   ├── server.py              # FastAPI application
│   ├── face_detection.py      # Face detection & mask classification
│   ├── video_processor.py     # Video stream processing
│   ├── detection_manager.py   # Detection data management
│   ├── websocket_manager.py   # WebSocket connections
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx   # Main dashboard component
│   │   │   ├── WebcamCapture.jsx # Camera handling
│   │   │   └── ui/             # Shadcn UI components
│   │   ├── hooks/
│   │   │   └── use-toast.js    # Toast notifications
│   │   └── mock/
│   │       └── detectionData.js # Mock data for development
│   ├── package.json           # Node.js dependencies
│   └── tailwind.config.js     # TailwindCSS configuration
├── contracts.md              # API contracts documentation
├── test_result.md           # Testing results and protocols
└── README.md                # This file
```

## 🎯 Key Features Explained

### 1. Real-time Face Detection
- Uses OpenCV's Haar Cascade classifier for efficient face detection
- Processes video frames at 30 FPS with optimized performance
- Handles multiple faces in a single frame
- Adjustable detection sensitivity and minimum face size

### 2. Mask Classification
- CNN-based deep learning model for binary classification
- Input preprocessing: resize to 128x128, normalization
- Confidence scoring with calibrated probability outputs
- Mock implementation included for demo purposes

### 3. Professional Dashboard
- Real-time statistics with animated counters
- Interactive progress bars and compliance meters
- Color-coded detection overlays (Green=Mask, Red=No Mask)
- Responsive design for all screen sizes

### 4. Alert System
- Configurable visual and audio alerts
- Threshold-based alert triggering
- Cooldown periods to prevent alert spam
- WebSocket-powered real-time notifications

## 🧪 Testing

### Run Frontend Tests
```bash
cd frontend
yarn test
```

### Run Backend Tests
```bash
cd backend
pytest tests/
```

### Manual Testing Checklist
- [ ] Dashboard loads with proper styling
- [ ] WebSocket connection establishes successfully
- [ ] Start/Stop detection buttons function correctly
- [ ] Statistics update in real-time
- [ ] Settings changes persist correctly
- [ ] Alert notifications display properly
- [ ] Video stream displays without errors

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=face_mask_detection
DEBUG=true
```

#### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Customization Options

#### Detection Sensitivity
Modify face detection parameters in `face_detection.py`:
```python
faces = self.face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,      # Adjust for detection sensitivity
    minNeighbors=5,       # Minimum neighbor rectangles
    minSize=(30, 30),     # Minimum face size
)
```

#### UI Theming
Customize colors and styling in `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: 'your-color-here',
      // ... other customizations
    }
  }
}
```

## 🚀 Deployment Options

### Cloud Platforms
- **Vercel/Netlify**: Frontend deployment
- **Heroku/Railway**: Backend API deployment
- **MongoDB Atlas**: Managed database
- **AWS/GCP/Azure**: Full-stack deployment

### Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://mongo:27017
    depends_on:
      - mongo
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
  
  mongo:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow ESLint rules for JavaScript/React code
- Use Black formatter for Python code
- Write tests for new features
- Update documentation for API changes
- Ensure mobile responsiveness for UI changes

### Code Style
- **Frontend**: Prettier + ESLint configuration
- **Backend**: Black + flake8 for Python formatting
- **Commits**: Follow conventional commit format

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenCV Community** - Computer vision library
- **TensorFlow Team** - Deep learning framework
- **FastAPI** - High-performance web framework
- **React Team** - Frontend framework
- **Shadcn/ui** - Component library
- **TailwindCSS** - Utility-first CSS framework


## 🗺️ Roadmap

### Version 2.0
- [ ] Advanced mask type detection (N95, surgical, cloth)
- [ ] Face recognition for individual tracking
- [ ] Multi-camera support
- [ ] Advanced analytics and reporting
- [ ] Mobile app companion

### Version 1.1
- [ ] Improved accuracy with larger training dataset
- [ ] Email/SMS alert integration
- [ ] Data export to CSV/PDF
- [ ] Admin panel for user management
- [ ] API rate limiting and authentication

---

**Built with ❤️ by [Om Deshpande](https://github.com/omdeshpande09012005)**

*Making public spaces safer through AI-powered compliance monitoring.*
