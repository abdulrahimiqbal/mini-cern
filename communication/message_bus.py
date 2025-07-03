"""
Message Bus System - Redis Streams-based Inter-Agent Communication
Handles real-time messaging between research agents
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import redis.asyncio as redis
from uuid import uuid4

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages in the system"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    STATUS_UPDATE = "status_update"
    ERROR_NOTIFICATION = "error_notification"
    RESEARCH_DATA = "research_data"
    SYSTEM_EVENT = "system_event"
    HEARTBEAT = "heartbeat"
    EMERGENCY_STOP = "emergency_stop"

@dataclass
class AgentMessage:
    """Standard message format for agent communication"""
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast messages
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 0  # 0=normal, 1=high, 2=critical
    correlation_id: Optional[str] = None  # For request/response tracking
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['message_type'] = self.message_type.value
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create from dictionary loaded from Redis"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['message_type'] = MessageType(data['message_type'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)

class MessageBus:
    """Redis Streams-based message bus for agent communication"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.subscribers: Dict[str, List[Callable]] = {}  # stream -> [handlers]
        self.consumer_groups: Dict[str, str] = {}  # stream -> group_name
        self.is_running = False
        self.consumer_tasks: List[asyncio.Task] = []
        
        # Stream names
        self.streams = {
            "agent_communication": "agent_comm",
            "task_coordination": "task_coord",
            "system_events": "sys_events",
            "research_data": "research_data",
            "emergency": "emergency"
        }
        
        # Message routing rules
        self.routing_rules = {
            MessageType.TASK_REQUEST: "task_coordination",
            MessageType.TASK_RESPONSE: "task_coordination",
            MessageType.COLLABORATION_REQUEST: "agent_communication",
            MessageType.COLLABORATION_RESPONSE: "agent_communication",
            MessageType.STATUS_UPDATE: "agent_communication",
            MessageType.RESEARCH_DATA: "research_data",
            MessageType.SYSTEM_EVENT: "system_events",
            MessageType.EMERGENCY_STOP: "emergency",
            MessageType.ERROR_NOTIFICATION: "system_events",
            MessageType.HEARTBEAT: "agent_communication"
        }
    
    async def initialize(self) -> None:
        """Initialize the message bus"""
        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            
            # Create consumer groups for each stream
            for stream_name, stream_key in self.streams.items():
                try:
                    await self.redis.xgroup_create(stream_key, f"{stream_name}_group", id='0', mkstream=True)
                    self.consumer_groups[stream_key] = f"{stream_name}_group"
                except redis.exceptions.ResponseError as e:
                    if "BUSYGROUP" in str(e):
                        # Group already exists
                        self.consumer_groups[stream_key] = f"{stream_name}_group"
                    else:
                        raise
            
            self.is_running = True
            logger.info("Message bus initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize message bus: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the message bus"""
        self.is_running = False
        
        # Cancel all consumer tasks
        for task in self.consumer_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        if self.redis:
            await self.redis.close()
        
        logger.info("Message bus shutdown complete")
    
    async def publish(self, message: AgentMessage) -> str:
        """Publish a message to the appropriate stream"""
        if not self.redis:
            raise RuntimeError("Message bus not initialized")
        
        # Determine target stream
        stream_name = self.routing_rules.get(message.message_type, "agent_communication")
        stream_key = self.streams.get(stream_name, "agent_comm")
        
        # Add message to stream
        message_data = message.to_dict()
        message_id = await self.redis.xadd(stream_key, message_data)
        
        logger.debug(f"Published message {message.message_id} to {stream_key}")
        return message_id
    
    async def subscribe(self, stream_name: str, handler: Callable[[AgentMessage], None], consumer_id: str) -> None:
        """Subscribe to a message stream"""
        if stream_name not in self.streams:
            raise ValueError(f"Unknown stream: {stream_name}")
        
        if stream_name not in self.subscribers:
            self.subscribers[stream_name] = []
        
        self.subscribers[stream_name].append(handler)
        
        # Start consumer task if not already running
        stream_key = self.streams[stream_name]
        consumer_task = asyncio.create_task(
            self._consume_messages(stream_key, consumer_id, handler)
        )
        self.consumer_tasks.append(consumer_task)
        
        logger.info(f"Subscribed to {stream_name} with consumer {consumer_id}")
    
    async def _consume_messages(self, stream_key: str, consumer_id: str, handler: Callable) -> None:
        """Consume messages from a stream"""
        group_name = self.consumer_groups[stream_key]
        
        while self.is_running:
            try:
                # Read messages from stream
                messages = await self.redis.xreadgroup(
                    group_name,
                    consumer_id,
                    {stream_key: '>'},
                    count=10,
                    block=1000  # 1 second timeout
                )
                
                for stream, msgs in messages:
                    for message_id, fields in msgs:
                        try:
                            # Parse message
                            message = AgentMessage.from_dict(fields)
                            
                            # Check if message has expired
                            if message.expires_at and datetime.utcnow() > message.expires_at:
                                logger.warning(f"Message {message.message_id} expired, skipping")
                                await self.redis.xack(stream_key, group_name, message_id)
                                continue
                            
                            # Call handler
                            await handler(message)
                            
                            # Acknowledge message
                            await self.redis.xack(stream_key, group_name, message_id)
                            
                        except Exception as e:
                            logger.error(f"Error processing message {message_id}: {e}")
                            # Message will be retried by Redis
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message consumer: {e}")
                await asyncio.sleep(1)  # Brief pause before retry
    
    async def send_task_request(self, sender_id: str, recipient_id: str, task_data: Dict[str, Any]) -> str:
        """Send a task request to another agent"""
        message = AgentMessage(
            message_id=str(uuid4()),
            message_type=MessageType.TASK_REQUEST,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=task_data,
            timestamp=datetime.utcnow(),
            priority=1,
            correlation_id=str(uuid4())
        )
        
        return await self.publish(message)
    
    async def send_collaboration_request(self, sender_id: str, recipient_id: str, collaboration_data: Dict[str, Any]) -> str:
        """Send a collaboration request to another agent"""
        message = AgentMessage(
            message_id=str(uuid4()),
            message_type=MessageType.COLLABORATION_REQUEST,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=collaboration_data,
            timestamp=datetime.utcnow(),
            correlation_id=str(uuid4())
        )
        
        return await self.publish(message)
    
    async def broadcast_status_update(self, sender_id: str, status_data: Dict[str, Any]) -> str:
        """Broadcast status update to all agents"""
        message = AgentMessage(
            message_id=str(uuid4()),
            message_type=MessageType.STATUS_UPDATE,
            sender_id=sender_id,
            recipient_id=None,  # Broadcast
            content=status_data,
            timestamp=datetime.utcnow()
        )
        
        return await self.publish(message)
    
    async def send_emergency_stop(self, sender_id: str, reason: str) -> str:
        """Send emergency stop signal"""
        message = AgentMessage(
            message_id=str(uuid4()),
            message_type=MessageType.EMERGENCY_STOP,
            sender_id=sender_id,
            recipient_id=None,  # Broadcast
            content={"reason": reason, "timestamp": datetime.utcnow().isoformat()},
            timestamp=datetime.utcnow(),
            priority=2  # Critical
        )
        
        return await self.publish(message)
    
    async def get_stream_info(self, stream_name: str) -> Dict[str, Any]:
        """Get information about a stream"""
        if stream_name not in self.streams:
            raise ValueError(f"Unknown stream: {stream_name}")
        
        stream_key = self.streams[stream_name]
        info = await self.redis.xinfo_stream(stream_key)
        
        return {
            "length": info.get("length", 0),
            "consumers": info.get("groups", 0),
            "last_generated_id": info.get("last-generated-id"),
            "first_entry": info.get("first-entry"),
            "last_entry": info.get("last-entry")
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        status = {
            "is_running": self.is_running,
            "active_consumers": len(self.consumer_tasks),
            "streams": {}
        }
        
        for stream_name in self.streams.keys():
            try:
                status["streams"][stream_name] = await self.get_stream_info(stream_name)
            except Exception as e:
                status["streams"][stream_name] = {"error": str(e)}
        
        return status 