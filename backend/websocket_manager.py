import asyncio
import json
import logging
from typing import Dict, List, Set
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocketServerProtocol] = set()
        
    async def connect(self, websocket: WebSocketServerProtocol):
        """Add a new WebSocket connection"""
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_to_connection(websocket, {
            'type': 'connection_established',
            'message': 'Connected to Face Mask Detection System'
        })
    
    async def disconnect(self, websocket: WebSocketServerProtocol):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_to_connection(self, websocket: WebSocketServerProtocol, data: Dict):
        """Send data to a specific connection"""
        try:
            message = json.dumps(data) if isinstance(data, dict) else str(data)
            await websocket.send(message)
        except ConnectionClosed:
            logger.warning("Tried to send to closed connection")
            self.active_connections.discard(websocket)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.active_connections.discard(websocket)
    
    async def broadcast(self, data: Dict):
        """Broadcast data to all active connections"""
        if not self.active_connections:
            return
        
        message = json.dumps(data)
        disconnected = set()
        
        for websocket in self.active_connections:
            try:
                await websocket.send(message)
            except ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected connections
        for websocket in disconnected:
            self.active_connections.discard(websocket)
        
        if disconnected:
            logger.info(f"Removed {len(disconnected)} disconnected connections")
    
    async def send_detection_update(self, detections: List[Dict]):
        """Send detection update to all connections"""
        await self.broadcast({
            'type': 'detection_update',
            'data': detections
        })
    
    async def send_statistics_update(self, statistics: Dict):
        """Send statistics update to all connections"""
        await self.broadcast({
            'type': 'statistics_update',
            'data': statistics
        })
    
    async def send_alert(self, alert_data: Dict):
        """Send alert to all connections"""
        await self.broadcast({
            'type': 'alert_triggered',
            'data': alert_data
        })
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)