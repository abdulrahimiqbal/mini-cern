"""
Science Research Institute - Agent Communication Framework
Real-time messaging and collaboration infrastructure for research agents
"""

# Use mock implementations for testing (no Redis dependency)
from .message_bus_mock import MessageBus, MessageType, AgentMessage
from .agent_registry_mock import AgentRegistry, RegistryEntry, RegistrationStatus

# Define mock protocols for testing
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass 
class TaskHandoff:
    handoff_id: str
    source_agent_id: str
    target_agent_id: str
    task_type: str
    task_data: Dict[str, Any]
    required_capabilities: List
    priority: TaskPriority

@dataclass
class ResearchWorkflow:
    workflow_id: str
    workflow_type: str
    participants: List[str]
    status: str
    current_step: int
    total_steps: int

class CollaborationProtocol:
    def __init__(self, message_bus, agent_registry):
        self.message_bus = message_bus
        self.agent_registry = agent_registry
        self.active_workflows = {}
    
    async def initiate_task_handoff(self, handoff):
        return True
    
    async def start_workflow(self, workflow_type, participants, context=None):
        workflow_id = f"workflow_{len(self.active_workflows) + 1}"
        self.active_workflows[workflow_id] = {
            "workflow_type": workflow_type,
            "participants": participants,
            "total_steps": 6 if workflow_type == "full_research_cycle" else 3
        }
        return workflow_id
    
    async def get_workflow_status(self, workflow_id):
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                "workflow_type": workflow["workflow_type"],
                "participants": workflow["participants"],
                "total_steps": workflow["total_steps"]
            }
        return None

__all__ = [
    'MessageBus',
    'MessageType', 
    'AgentMessage',
    'AgentRegistry',
    'RegistryEntry',
    'RegistrationStatus',
    'CollaborationProtocol',
    'TaskHandoff',
    'ResearchWorkflow',
    'TaskPriority'
] 