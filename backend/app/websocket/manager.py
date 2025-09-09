"""
WebSocket Connection Manager
Handles real-time connections for job progress updates and notifications
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import json
import asyncio
from ..core.logging import get_logger

logger = get_logger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, List[str]] = {}  # user_id -> connection_ids
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str = None):
        """Accept WebSocket connection and register it"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id} (user: {user_id})")
    
    def disconnect(self, connection_id: str, user_id: str = None):
        """Remove connection from active connections"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id] = [
                cid for cid in self.user_connections[user_id] if cid != connection_id
            ]
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected: {connection_id} (user: {user_id})")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def send_user_message(self, message: dict, user_id: str):
        """Send message to all connections for a specific user"""
        if user_id in self.user_connections:
            connection_ids = self.user_connections[user_id].copy()
            for connection_id in connection_ids:
                await self.send_personal_message(message, connection_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all active connections"""
        connection_ids = list(self.active_connections.keys())
        for connection_id in connection_ids:
            await self.send_personal_message(message, connection_id)
    
    async def send_job_update(self, user_id: str, job_update: dict):
        """Send job progress update to user"""
        message = {
            "type": "job_update",
            "data": job_update
        }
        await self.send_user_message(message, user_id)
    
    async def send_dataset_update(self, user_id: str, dataset_update: dict):
        """Send dataset status update to user"""
        message = {
            "type": "dataset_update",
            "data": dataset_update
        }
        await self.send_user_message(message, user_id)
    
    async def send_analysis_complete(self, user_id: str, analysis_results: dict):
        """Send analysis completion notification"""
        message = {
            "type": "analysis_complete",
            "data": analysis_results
        }
        await self.send_user_message(message, user_id)
    
    async def send_error_notification(self, user_id: str, error_details: dict):
        """Send error notification to user"""
        message = {
            "type": "error",
            "data": error_details
        }
        await self.send_user_message(message, user_id)
    
    async def disconnect_all(self):
        """Disconnect all active connections (for shutdown)"""
        connection_ids = list(self.active_connections.keys())
        for connection_id in connection_ids:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing connection {connection_id}: {e}")
        
        self.active_connections.clear()
        self.user_connections.clear()
        logger.info("All WebSocket connections closed")
    
    def get_connection_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "unique_users": len(self.user_connections),
            "connections_per_user": {
                user_id: len(connections) 
                for user_id, connections in self.user_connections.items()
            }
        }

# Global connection manager instance
connection_manager = ConnectionManager()
