"""
Mock Message Bus - Testing Implementation Without Redis
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
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
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['message_type'] = self.message_type.value
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['message_type'] = MessageType(data['message_type'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)

class MessageBus:
    """Mock message bus for testing"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.messages: List[AgentMessage] = []  # Store messages in memory
        self.subscribers: Dict[str, List[Callable]] = {}
        self.is_running = False
        
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
        """Initialize the mock message bus"""
        self.is_running = True
        logger.info("Mock message bus initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the mock message bus"""
        self.is_running = False
        logger.info("Mock message bus shutdown")
    
    async def publish(self, message: AgentMessage) -> str:
        """Publish a message"""
        self.messages.append(message)
        logger.debug(f"Published message {message.message_id}")
        return f"mock_id_{len(self.messages)}"
    
    async def send_task_request(self, sender_id: str, recipient_id: str, task_data: Dict[str, Any]) -> str:
        """Send a task request"""
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
        """Send a collaboration request"""
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