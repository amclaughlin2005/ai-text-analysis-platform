"""
WebSocket Event Handlers
Provides WebSocket endpoints for real-time communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
import uuid
import json
from typing import Optional
from .manager import connection_manager
from ..core.logging import get_logger, set_correlation_id

logger = get_logger(__name__)
router = APIRouter()

@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: Optional[str] = Query(None)
):
    """Main WebSocket connection endpoint"""
    connection_id = str(uuid.uuid4())
    set_correlation_id(connection_id)
    
    try:
        await connection_manager.connect(websocket, connection_id, user_id)
        
        # Send welcome message
        welcome_message = {
            "type": "connection_established",
            "data": {
                "connection_id": connection_id,
                "message": "WebSocket connection established",
                "supported_events": [
                    "job_update", "dataset_update", "analysis_complete", 
                    "error", "ping", "pong"
                ]
            }
        }
        await connection_manager.send_personal_message(welcome_message, connection_id)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                await handle_websocket_message(message, connection_id, user_id)
                
            except json.JSONDecodeError:
                error_message = {
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                }
                await connection_manager.send_personal_message(error_message, connection_id)
                
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                error_message = {
                    "type": "error",
                    "data": {"message": "Error processing message"}
                }
                await connection_manager.send_personal_message(error_message, connection_id)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        connection_manager.disconnect(connection_id, user_id)

async def handle_websocket_message(message: dict, connection_id: str, user_id: str = None):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Respond to ping with pong
        pong_message = {
            "type": "pong",
            "data": {"timestamp": message.get("data", {}).get("timestamp")}
        }
        await connection_manager.send_personal_message(pong_message, connection_id)
        
    elif message_type == "subscribe":
        # Handle subscription to specific events
        subscriptions = message.get("data", {}).get("events", [])
        response = {
            "type": "subscription_confirmed",
            "data": {"subscribed_events": subscriptions}
        }
        await connection_manager.send_personal_message(response, connection_id)
        
    elif message_type == "unsubscribe":
        # Handle unsubscription from events
        unsubscriptions = message.get("data", {}).get("events", [])
        response = {
            "type": "unsubscription_confirmed",
            "data": {"unsubscribed_events": unsubscriptions}
        }
        await connection_manager.send_personal_message(response, connection_id)
        
    elif message_type == "get_stats":
        # Send connection statistics
        stats = connection_manager.get_connection_stats()
        response = {
            "type": "stats",
            "data": stats
        }
        await connection_manager.send_personal_message(response, connection_id)
        
    else:
        # Unknown message type
        error_response = {
            "type": "error",
            "data": {
                "message": f"Unknown message type: {message_type}",
                "supported_types": ["ping", "subscribe", "unsubscribe", "get_stats"]
            }
        }
        await connection_manager.send_personal_message(error_response, connection_id)

# Additional WebSocket endpoints for specific purposes
@router.websocket("/jobs/{job_id}")
async def job_specific_websocket(
    websocket: WebSocket,
    job_id: str,
    user_id: Optional[str] = Query(None)
):
    """WebSocket endpoint for specific job updates"""
    connection_id = f"job-{job_id}-{str(uuid.uuid4())[:8]}"
    set_correlation_id(connection_id)
    
    try:
        await connection_manager.connect(websocket, connection_id, user_id)
        
        # Send job-specific welcome message
        welcome_message = {
            "type": "job_connection_established",
            "data": {
                "connection_id": connection_id,
                "job_id": job_id,
                "message": f"Connected to job {job_id} updates"
            }
        }
        await connection_manager.send_personal_message(welcome_message, connection_id)
        
        # Keep connection alive
        while True:
            try:
                # Just receive and echo back for now (ping/pong)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    pong_message = {
                        "type": "pong",
                        "data": {"job_id": job_id}
                    }
                    await connection_manager.send_personal_message(pong_message, connection_id)
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error in job WebSocket: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"Job WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"Job WebSocket error: {e}")
    finally:
        connection_manager.disconnect(connection_id, user_id)
