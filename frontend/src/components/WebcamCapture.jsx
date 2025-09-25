import React, { useRef, useEffect, useState } from 'react';
import { Camera, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';
import { useToast } from '../hooks/use-toast';

const WebcamCapture = ({ isActive, onDetection, children }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (isActive) {
      startWebcam();
    } else {
      stopWebcam();
    }

    return () => {
      stopWebcam();
    };
  }, [isActive]);

  const startWebcam = async () => {
    setIsLoading(true);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        setStream(mediaStream);
        
        // Start detection simulation
        simulateDetection();
      }

      toast({
        title: "Camera Connected",
        description: "Webcam feed active - detection ready",
      });
    } catch (error) {
      console.error('Error accessing webcam:', error);
      toast({
        title: "Camera Error",
        description: "Unable to access webcam. Please check permissions and try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const stopWebcam = () => {
    if (stream) {
      stream.getTracks().forEach(track => {
        track.stop();
      });
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const simulateDetection = () => {
    // Mock detection - will be replaced with real AI detection
    const mockDetections = [
      { x: 150, y: 120, w: 100, h: 120, hasMask: true, confidence: 0.94 },
      { x: 350, y: 200, w: 95, h: 115, hasMask: false, confidence: 0.89 },
      { x: 280, y: 180, w: 88, h: 105, hasMask: true, confidence: 0.97 }
    ];

    if (onDetection) {
      setTimeout(() => {
        onDetection(mockDetections);
      }, 2000);
    }
  };

  const retryConnection = () => {
    stopWebcam();
    setTimeout(() => {
      if (isActive) {
        startWebcam();
      }
    }, 1000);
  };

  return (
    <div className="relative w-full h-full bg-black rounded-lg overflow-hidden">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 z-10">
          <div className="text-center text-white">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2" />
            <p>Connecting to camera...</p>
          </div>
        </div>
      )}

      {!isActive && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <Camera className="h-16 w-16 mx-auto mb-4 opacity-50" />
            <p className="mb-4">Camera feed inactive</p>
            <Button onClick={startWebcam} variant="outline" size="sm">
              <Camera className="h-4 w-4 mr-2" />
              Start Camera
            </Button>
          </div>
        </div>
      )}

      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className={`w-full h-full object-cover ${!isActive ? 'hidden' : ''}`}
        onError={() => {
          toast({
            title: "Video Error",
            description: "There was an issue with the video stream.",
            variant: "destructive"
          });
        }}
      />

      <canvas
        ref={canvasRef}
        className="hidden"
        width={640}
        height={480}
      />

      {/* Detection overlay */}
      {children}

      {stream && isActive && (
        <div className="absolute bottom-4 right-4">
          <Button
            onClick={retryConnection}
            variant="secondary"
            size="sm"
            className="bg-black bg-opacity-50 hover:bg-opacity-70"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default WebcamCapture;