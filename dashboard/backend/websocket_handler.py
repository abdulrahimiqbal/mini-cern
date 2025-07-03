"""
WebSocket Handler for Real-time Dashboard Communication
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime


logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and real-time event broadcasting"""
    
    def __init__(self):
        # Connected clients tracking
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.client_subscriptions: Dict[str, Set[str]] = {}
        
        # Message queue for offline clients
        self.message_queue: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info("WebSocket manager initialized")
    
    async def connect_client(self, client_id: str, client_info: Dict[str, Any]):
        """Handle client connection"""
        try:
            self.connected_clients[client_id] = {
                **client_info,
                "connected_at": datetime.now(),
                "last_activity": datetime.now()
            }
            self.client_subscriptions[client_id] = set()
            
            logger.info(f"Client connected: {client_id}")
            
            # Send any queued messages
            if client_id in self.message_queue:
                for message in self.message_queue[client_id]:
                    await self.send_to_client(client_id, message)
                del self.message_queue[client_id]
                
        except Exception as e:
            logger.error(f"Error handling client connection: {e}")
    
    async def disconnect_client(self, client_id: str):
        """Handle client disconnection"""
        try:
            if client_id in self.connected_clients:
                logger.info(f"Client disconnected: {client_id}")
                del self.connected_clients[client_id]
                
            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]
                
        except Exception as e:
            logger.error(f"Error handling client disconnection: {e}")
    
    async def broadcast(self, message: Dict[str, Any], event_type: Optional[str] = None):
        """Broadcast message to all connected clients"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = datetime.now().isoformat()
            
            # Simulate broadcasting (in real implementation, would send via WebSocket)
            logger.info(f"Broadcasting message to {len(self.connected_clients)} clients: {message.get('type', 'unknown')}")
            
            # Update client activity
            current_time = datetime.now()
            for client_id in self.connected_clients:
                self.connected_clients[client_id]["last_activity"] = current_time
                
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        try:
            if client_id in self.connected_clients:
                message['timestamp'] = datetime.now().isoformat()
                logger.debug(f"Sent message to client {client_id}")
                
                # Update last activity
                self.connected_clients[client_id]["last_activity"] = datetime.now()
            else:
                # Queue message for offline client
                if client_id not in self.message_queue:
                    self.message_queue[client_id] = []
                
                message['queued_at'] = datetime.now().isoformat()
                self.message_queue[client_id].append(message)
                
                logger.debug(f"Queued message for offline client {client_id}")
                
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {e}")
    
    async def get_connected_clients(self) -> Dict[str, Dict[str, Any]]:
        """Get information about connected clients"""
        return self.connected_clients.copy()
    
    async def get_client_count(self) -> int:
        """Get number of connected clients"""
        return len(self.connected_clients)
    
    async def disconnect_all(self):
        """Disconnect all clients"""
        try:
            clients = list(self.connected_clients.keys())
            for client_id in clients:
                await self.disconnect_client(client_id)
            
            logger.info(f"Disconnected all {len(clients)} clients")
            
        except Exception as e:
            logger.error(f"Error disconnecting all clients: {e}")
