"""
Science Research Institute - AI Agent Framework
Autonomous research agents with Virtuals Protocol integration
"""

from .base_agent import BaseAgent, AgentStatus, AgentTask, AgentResult
from .agent_types import AgentType, AgentCapability, ResearchRole
from .exceptions import AgentError, TaskExecutionError, CommunicationError

__all__ = [
    'BaseAgent', 
    'AgentStatus', 
    'AgentTask', 
    'AgentResult',
    'AgentType', 
    'AgentCapability', 
    'ResearchRole',
    'AgentError', 
    'TaskExecutionError', 
    'CommunicationError'
] 