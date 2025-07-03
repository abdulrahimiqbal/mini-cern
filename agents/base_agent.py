"""
Base Agent Class
Abstract base class for all research agents with Virtuals Protocol integration
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .agent_types import (
    AgentType, AgentCapability, AgentState, TaskType, TaskPriority,
    AgentCapabilities, AgentMetrics, VirtualsAgentConfig
)
from .exceptions import AgentError, AgentCapabilityError

logger = logging.getLogger(__name__)

@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.RESEARCH_PLANNING
    priority: TaskPriority = TaskPriority.MEDIUM
    title: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    project_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    required_capabilities: List[AgentCapability] = field(default_factory=list)
    reward_tokens: float = 0.0

@dataclass 
class AgentResult:
    """Result of an agent task execution"""
    task_id: str
    agent_id: str
    success: bool
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    confidence_score: float = 1.0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime = field(default_factory=datetime.utcnow)
    tokens_earned: float = 0.0

@dataclass
class AgentStatus:
    """Current status of an agent"""
    agent_id: str
    state: AgentState
    current_task_id: Optional[str] = None
    uptime_hours: float = 0.0
    success_rate: float = 1.0
    token_balance: float = 0.0
    reputation_score: float = 100.0

class BaseAgent(ABC):
    """Abstract base class for all research agents"""
    
    def __init__(
        self, 
        agent_id: str,
        agent_type: AgentType,
        capabilities: AgentCapabilities,
        virtuals_config: Optional[VirtualsAgentConfig] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.state = AgentState.IDLE
        self.current_task: Optional[AgentTask] = None
        self.metrics = AgentMetrics()
        self.start_time = datetime.utcnow()
        
        # Virtuals Protocol integration
        self.virtuals_config = virtuals_config or VirtualsAgentConfig()
        if self.virtuals_config.agent_token_symbol is None:
            self.virtuals_config.agent_token_symbol = f"{agent_type.value.upper()}-{agent_id[:8]}"
        
        self.logger = logging.getLogger(f"agent.{agent_type.value}.{agent_id}")
        self.logger.info(f"Agent {agent_id} initialized")
    
    async def initialize(self) -> None:
        """Initialize the agent"""
        try:
            self.state = AgentState.INITIALIZING
            await self._agent_initialize()
            await self._initialize_virtuals_protocol()
            self.state = AgentState.IDLE
            self.logger.info(f"Agent {self.agent_id} ready")
        except Exception as e:
            self.state = AgentState.ERROR
            raise AgentError(f"Failed to initialize: {e}", self.agent_id)
    
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a research task"""
        if not self._can_execute_task(task):
            raise AgentCapabilityError(
                f"Cannot execute task {task.task_id}", 
                agent_id=self.agent_id
            )
        
        self.current_task = task
        self.state = AgentState.WORKING
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Executing task: {task.title}")
            result_data = await self._execute_task_implementation(task)
            
            result = AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                result_data=result_data,
                started_at=start_time,
                completed_at=datetime.utcnow()
            )
            
            await self._process_virtuals_rewards(task, result)
            await self._update_metrics(result)
            
            self.logger.info(f"Task completed: {task.task_id}")
            return result
            
        except Exception as e:
            result = AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error_message=str(e),
                started_at=start_time,
                completed_at=datetime.utcnow()
            )
            await self._update_metrics(result)
            self.logger.error(f"Task failed: {e}")
            return result
            
        finally:
            self.current_task = None
            self.state = AgentState.IDLE
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the agent"""
        self.logger.info(f"Shutting down agent {self.agent_id}")
        await self._agent_shutdown()
        self.state = AgentState.OFFLINE
    
    def get_status(self) -> AgentStatus:
        """Get current agent status"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds() / 3600
        return AgentStatus(
            agent_id=self.agent_id,
            state=self.state,
            current_task_id=self.current_task.task_id if self.current_task else None,
            uptime_hours=uptime,
            success_rate=self.metrics.success_rate,
            token_balance=self.metrics.tokens_earned,
            reputation_score=self.metrics.reputation_score
        )
    
    def can_handle_task(self, task: AgentTask) -> bool:
        """Check if agent can handle a task"""
        return self._can_execute_task(task)
    
    # Abstract methods to be implemented by subclasses
    @abstractmethod
    async def _agent_initialize(self) -> None:
        """Agent-specific initialization"""
        pass
    
    @abstractmethod
    async def _execute_task_implementation(self, task: AgentTask) -> Dict[str, Any]:
        """Execute the actual task"""
        pass
    
    async def _agent_shutdown(self) -> None:
        """Agent-specific shutdown logic"""
        pass
    
    # Helper methods
    def _can_execute_task(self, task: AgentTask) -> bool:
        """Check if agent has required capabilities"""
        agent_caps = set(self.capabilities.capabilities)
        required_caps = set(task.required_capabilities)
        return required_caps.issubset(agent_caps)
    
    async def _initialize_virtuals_protocol(self) -> None:
        """Initialize Virtuals Protocol connection"""
        if self.virtuals_config.revenue_sharing_enabled:
            self.logger.info(f"Virtuals Protocol enabled: {self.virtuals_config.agent_token_symbol}")
    
    async def _process_virtuals_rewards(self, task: AgentTask, result: AgentResult) -> None:
        """Process token rewards from Virtuals Protocol"""
        if result.success and self.virtuals_config.revenue_sharing_enabled:
            reward = task.reward_tokens
            self.metrics.tokens_earned += reward
            result.tokens_earned = reward
            self.logger.info(f"Earned {reward} tokens for task completion")
    
    async def _update_metrics(self, result: AgentResult) -> None:
        """Update agent performance metrics"""
        if result.success:
            self.metrics.tasks_completed += 1
        else:
            self.metrics.tasks_failed += 1
        
        self.metrics.update_success_rate()
        self.metrics.last_updated = datetime.utcnow() 