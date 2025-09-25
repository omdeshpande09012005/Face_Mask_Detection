import React, { useState, useRef, useEffect } from 'react';
import { Camera, AlertTriangle, CheckCircle, Settings, Play, Pause, Volume2, VolumeX, Users, Clock, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { useToast } from '../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [soundAlerts, setSoundAlerts] = useState(true);
  const [visualAlerts, setVisualAlerts] = useState(true);
  const [detections, setDetections] = useState([]);
  const [stats, setStats] = useState({
    totalDetections: 0,
    maskedCount: 0,
    unmaskedCount: 0,
    complianceRate: 0,
    avgConfidence: 0,
    activeAlerts: 0
  });
  const [wsConnected, setWsConnected] = useState(false);
  const videoRef = useRef(null);
  const wsRef = useRef(null);
  const { toast } = useToast();

  useEffect(() => {
    if (isStreaming) {
      startWebcam();
    } else {
      stopWebcam();
    }
    return () => stopWebcam();
  }, [isStreaming]);

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      toast({
        title: "Camera Error",
        description: "Unable to access webcam. Please check permissions.",
        variant: "destructive"
      });
      setIsStreaming(false);
    }
  };

  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  const toggleStreaming = () => {
    setIsStreaming(!isStreaming);
    if (!isStreaming) {
      toast({
        title: "Detection Started",
        description: "Face mask detection is now active",
      });
    }
  };

  const handleAlert = (detection) => {
    if (!detection.hasMask && visualAlerts) {
      toast({
        title: "⚠️ Mask Violation Detected",
        description: `${detection.person} is not wearing a mask (${Math.round(detection.confidence * 100)}% confidence)`,
        variant: "destructive"
      });
    }
  };

  const DetectionOverlay = () => (
    <div className="absolute inset-0 pointer-events-none">
      {detections.slice(0, 3).map((detection) => (
        <div
          key={detection.id}
          className={`absolute border-2 transition-all duration-200 ${
            detection.hasMask ? 'border-green-400' : 'border-red-400'
          }`}
          style={{
            left: `${detection.position.x}px`,
            top: `${detection.position.y}px`,
            width: `${detection.position.w}px`,
            height: `${detection.position.h}px`,
          }}
        >
          <div className={`absolute -top-8 left-0 px-2 py-1 text-xs font-medium rounded ${
            detection.hasMask 
              ? 'bg-green-500 text-white' 
              : 'bg-red-500 text-white'
          }`}>
            {detection.hasMask ? 'MASK' : 'NO MASK'} ({Math.round(detection.confidence * 100)}%)
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Face Mask Detection System</h1>
            <p className="text-gray-400 mt-2">Real-Time Compliance Monitoring Dashboard</p>
          </div>
          <div className="flex items-center space-x-4">
            <Badge variant={isStreaming ? "default" : "secondary"} className="px-3 py-1">
              {isStreaming ? "ACTIVE" : "INACTIVE"}
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Video Feed */}
          <div className="lg:col-span-2">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Camera className="h-5 w-5" />
                    <span>Live Camera Feed</span>
                  </div>
                  <Button
                    onClick={toggleStreaming}
                    variant={isStreaming ? "destructive" : "default"}
                    size="sm"
                  >
                    {isStreaming ? (
                      <>
                        <Pause className="h-4 w-4 mr-2" />
                        Stop
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Start
                      </>
                    )}
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
                  {isStreaming ? (
                    <>
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        className="w-full h-full object-cover"
                      />
                      <DetectionOverlay />
                    </>
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center text-gray-400">
                        <Camera className="h-16 w-16 mx-auto mb-4 opacity-50" />
                        <p>Click Start to begin face mask detection</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Statistics Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <Users className="h-5 w-5 text-blue-400" />
                    <div>
                      <p className="text-sm text-gray-400">Total Detected</p>
                      <p className="text-2xl font-bold">{stats.totalDetections}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                    <div>
                      <p className="text-sm text-gray-400">With Mask</p>
                      <p className="text-2xl font-bold text-green-400">{stats.maskedCount}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="h-5 w-5 text-red-400" />
                    <div>
                      <p className="text-sm text-gray-400">Without Mask</p>
                      <p className="text-2xl font-bold text-red-400">{stats.unmaskedCount}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5 text-purple-400" />
                    <div>
                      <p className="text-sm text-gray-400">Compliance</p>
                      <p className="text-2xl font-bold text-purple-400">{stats.complianceRate}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Controls */}
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span>Detection Controls</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Visual Alerts</label>
                  <Switch 
                    checked={visualAlerts} 
                    onCheckedChange={setVisualAlerts} 
                  />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Sound Alerts</label>
                  <Switch 
                    checked={soundAlerts} 
                    onCheckedChange={setSoundAlerts} 
                  />
                </div>
                <div className="pt-4">
                  <label className="text-sm font-medium mb-2 block">Compliance Rate</label>
                  <Progress 
                    value={stats.complianceRate} 
                    className="h-3" 
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    {stats.maskedCount} out of {stats.totalDetections} wearing masks
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Recent Detections */}
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="h-5 w-5" />
                  <span>Recent Detections</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {detections.map((detection) => (
                    <div 
                      key={detection.id}
                      className="flex items-center justify-between p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${
                          detection.hasMask ? 'bg-green-400' : 'bg-red-400'
                        }`} />
                        <div>
                          <p className="text-sm font-medium">{detection.person}</p>
                          <p className="text-xs text-gray-400">{detection.timestamp}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge 
                          variant={detection.hasMask ? "default" : "destructive"}
                          className="text-xs"
                        >
                          {detection.hasMask ? 'MASK' : 'NO MASK'}
                        </Badge>
                        <p className="text-xs text-gray-400 mt-1">
                          {Math.round(detection.confidence * 100)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Active Alerts */}
            {stats.activeAlerts > 0 && (
              <Card className="bg-red-900/20 border-red-700">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-red-400">
                    <AlertTriangle className="h-5 w-5" />
                    <span>Active Alerts ({stats.activeAlerts})</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Mask violations detected</span>
                      <Badge variant="destructive">HIGH</Badge>
                    </div>
                    <p className="text-xs text-gray-400">
                      Immediate attention required for compliance
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;