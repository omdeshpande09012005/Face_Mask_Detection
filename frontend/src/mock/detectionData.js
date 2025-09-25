// Mock data for face mask detection - will be replaced with real API calls
export const mockDetectionData = {
  // Live detection results
  currentDetections: [
    {
      id: 1,
      timestamp: new Date().toLocaleTimeString(),
      person: 'Person 1',
      hasMask: true,
      confidence: 0.94,
      position: { x: 150, y: 120, w: 100, h: 120 },
      alertTriggered: false
    },
    {
      id: 2,
      timestamp: new Date().toLocaleTimeString(),
      person: 'Person 2',
      hasMask: false,
      confidence: 0.89,
      position: { x: 350, y: 200, w: 95, h: 115 },
      alertTriggered: true
    },
    {
      id: 3,
      timestamp: new Date().toLocaleTimeString(),
      person: 'Person 3',
      hasMask: true,
      confidence: 0.97,
      position: { x: 280, y: 180, w: 88, h: 105 },
      alertTriggered: false
    }
  ],

  // Historical statistics
  statistics: {
    today: {
      totalDetections: 147,
      maskedCount: 112,
      unmaskedCount: 35,
      complianceRate: 76.2,
      avgConfidence: 0.92,
      peakHour: '14:00-15:00',
      alerts: 23
    },
    thisWeek: {
      totalDetections: 892,
      maskedCount: 734,
      unmaskedCount: 158,
      complianceRate: 82.3,
      avgConfidence: 0.89,
      bestDay: 'Tuesday',
      worstDay: 'Friday'
    }
  },

  // Detection history for logs
  detectionHistory: [
    { id: 1, timestamp: '14:32:15', person: 'Person 1', hasMask: true, confidence: 0.94 },
    { id: 2, timestamp: '14:31:45', person: 'Person 2', hasMask: false, confidence: 0.89 },
    { id: 3, timestamp: '14:31:12', person: 'Person 3', hasMask: true, confidence: 0.97 },
    { id: 4, timestamp: '14:30:58', person: 'Person 4', hasMask: false, confidence: 0.85 },
    { id: 5, timestamp: '14:30:33', person: 'Person 5', hasMask: true, confidence: 0.91 },
    { id: 6, timestamp: '14:30:02', person: 'Person 6', hasMask: true, confidence: 0.88 },
    { id: 7, timestamp: '14:29:41', person: 'Person 7', hasMask: false, confidence: 0.92 },
    { id: 8, timestamp: '14:29:18', person: 'Person 8', hasMask: true, confidence: 0.95 }
  ],

  // Alert configurations
  alertSettings: {
    visualAlerts: true,
    soundAlerts: true,
    emailNotifications: false,
    thresholdConfidence: 0.8,
    alertCooldown: 5000 // 5 seconds
  },

  // System status
  systemStatus: {
    cameraConnected: true,
    modelLoaded: true,
    processingSpeed: '15 fps',
    lastUpdate: new Date().toISOString(),
    errors: []
  }
};

// Mock API functions that will be replaced with real backend calls
export const mockAPI = {
  startDetection: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true, message: 'Detection started successfully' });
      }, 1000);
    });
  },

  stopDetection: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true, message: 'Detection stopped successfully' });
      }, 500);
    });
  },

  getStatistics: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockDetectionData.statistics);
      }, 300);
    });
  },

  getDetectionHistory: (limit = 50) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockDetectionData.detectionHistory.slice(0, limit));
      }, 200);
    });
  },

  updateSettings: (settings) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Mock update - in real app this would save to backend
        Object.assign(mockDetectionData.alertSettings, settings);
        resolve({ success: true, settings: mockDetectionData.alertSettings });
      }, 400);
    });
  },

  exportData: (format = 'json') => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const data = {
          exportDate: new Date().toISOString(),
          statistics: mockDetectionData.statistics,
          detectionHistory: mockDetectionData.detectionHistory
        };
        resolve({ 
          success: true, 
          data: format === 'json' ? JSON.stringify(data, null, 2) : data 
        });
      }, 800);
    });
  }
};