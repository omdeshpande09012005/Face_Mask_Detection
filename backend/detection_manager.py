import time
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from collections import deque
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
import asyncio

logger = logging.getLogger(__name__)

class DetectionManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.detection_history = deque(maxlen=1000)  # Keep last 1000 detections in memory
        self.statistics = {
            'totalDetections': 0,
            'maskedCount': 0,
            'unmaskedCount': 0,
            'complianceRate': 0.0,
            'avgConfidence': 0.0,
            'activeAlerts': 0,
            'lastUpdate': datetime.utcnow().isoformat()
        }
        self.settings = {
            'visualAlerts': True,
            'soundAlerts': True,
            'confidenceThreshold': 0.8,
            'alertCooldown': 5000  # 5 seconds
        }
        self.last_alert_time = {}  # Track last alert time for each detection
    
    async def process_detections(self, detections: List[Dict]) -> List[Dict]:
        """Process new detections and update statistics"""
        processed_detections = []
        
        for detection in detections:
            # Add unique ID and timestamp
            detection_id = str(uuid.uuid4())
            detection['id'] = detection_id
            detection['timestamp'] = datetime.utcnow().isoformat()
            detection['alertTriggered'] = False
            
            # Check if alert should be triggered
            if not detection['hasMask'] and detection['confidence'] >= self.settings['confidenceThreshold']:
                current_time = time.time() * 1000  # Convert to milliseconds
                last_alert = self.last_alert_time.get(detection_id, 0)
                
                if current_time - last_alert >= self.settings['alertCooldown']:
                    detection['alertTriggered'] = True
                    self.last_alert_time[detection_id] = current_time
                    self.statistics['activeAlerts'] += 1
            
            # Add to history
            self.detection_history.append(detection.copy())
            processed_detections.append(detection)
            
            # Save to database
            try:
                await self.db.detections.insert_one(detection.copy())
            except Exception as e:
                logger.error(f"Error saving detection to database: {e}")
        
        # Update statistics
        await self.update_statistics()
        
        return processed_detections
    
    async def update_statistics(self):
        """Update detection statistics"""
        try:
            # Calculate statistics from recent detections
            total_detections = len(self.detection_history)
            
            if total_detections == 0:
                return
            
            masked_count = sum(1 for d in self.detection_history if d['hasMask'])
            unmasked_count = total_detections - masked_count
            compliance_rate = (masked_count / total_detections) * 100 if total_detections > 0 else 0
            avg_confidence = sum(d['confidence'] for d in self.detection_history) / total_detections
            
            self.statistics.update({
                'totalDetections': total_detections,
                'maskedCount': masked_count,
                'unmaskedCount': unmasked_count,
                'complianceRate': round(compliance_rate, 2),
                'avgConfidence': round(avg_confidence, 3),
                'lastUpdate': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    def get_statistics(self) -> Dict:
        """Get current statistics"""
        return self.statistics.copy()
    
    def get_detection_history(self, limit: int = 50) -> List[Dict]:
        """Get recent detection history"""
        history = list(self.detection_history)
        return history[-limit:] if limit < len(history) else history
    
    async def get_detection_history_from_db(self, limit: int = 100) -> List[Dict]:
        """Get detection history from database"""
        try:
            cursor = self.db.detections.find().sort('timestamp', -1).limit(limit)
            detections = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for detection in detections:
                if '_id' in detection:
                    detection['_id'] = str(detection['_id'])
            
            return detections
        except Exception as e:
            logger.error(f"Error fetching detection history from database: {e}")
            return []
    
    def get_settings(self) -> Dict:
        """Get current settings"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict) -> Dict:
        """Update settings"""
        try:
            self.settings.update(new_settings)
            logger.info(f"Settings updated: {self.settings}")
            return self.settings.copy()
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return self.settings.copy()
    
    def clear_alerts(self):
        """Clear active alerts"""
        self.statistics['activeAlerts'] = 0
        self.last_alert_time.clear()
    
    async def cleanup_old_detections(self, days: int = 7):
        """Clean up old detections from database"""
        try:
            cutoff_date = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
            result = await self.db.detections.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            logger.info(f"Cleaned up {result.deleted_count} old detections")
        except Exception as e:
            logger.error(f"Error cleaning up old detections: {e}")