"""
Collaboration Protocols - Standardized Agent Interaction Patterns
Defines communication patterns and workflows for research agents
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4

from .message_bus import MessageBus, MessageType, AgentMessage
from .agent_registry import AgentRegistry
from agents.agent_types import AgentType, AgentCapability

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Status of a research workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class TaskHandoff:
    """Represents a task being handed off between agents"""
    handoff_id: str
    source_agent_id: str
    target_agent_id: str
    task_type: str
    task_data: Dict[str, Any]
    required_capabilities: List[AgentCapability]
    priority: TaskPriority
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.context is None:
            self.context = {}

@dataclass
class ResearchWorkflow:
    """Represents a multi-agent research workflow"""
    workflow_id: str
    workflow_type: str
    participants: List[str]  # Agent IDs
    status: WorkflowStatus
    current_step: int
    total_steps: int
    context: Dict[str, Any]
    results: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    coordinator_id: Optional[str] = None

class CollaborationProtocol:
    """Manages collaboration protocols between research agents"""
    
    def __init__(self, message_bus: MessageBus, agent_registry: AgentRegistry):
        self.message_bus = message_bus
        self.agent_registry = agent_registry
        self.active_workflows: Dict[str, ResearchWorkflow] = {}
        self.workflow_handlers: Dict[str, Callable] = {}
        self.task_timeout = 300  # 5 minutes default timeout
        
        # Register default workflow types
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Register default research workflow patterns"""
        self.workflow_handlers.update({
            "hypothesis_to_experiment": self._handle_hypothesis_to_experiment,
            "experiment_to_analysis": self._handle_experiment_to_analysis,
            "full_research_cycle": self._handle_full_research_cycle,
            "literature_review": self._handle_literature_review,
            "peer_review": self._handle_peer_review
        })
    
    async def initiate_task_handoff(self, handoff: TaskHandoff) -> bool:
        """Initiate a task handoff between agents"""
        try:
            # Check if target agent is available and capable
            target_agent = await self.agent_registry.get_agent(handoff.target_agent_id)
            if not target_agent:
                logger.error(f"Target agent {handoff.target_agent_id} not found")
                return False
            
            # Verify capabilities
            agent_caps = set(target_agent.capabilities)
            required_caps = set(handoff.required_capabilities)
            
            if not required_caps.issubset(agent_caps):
                logger.error(f"Agent {handoff.target_agent_id} lacks required capabilities")
                return False
            
            # Send task request message
            await self.message_bus.send_task_request(
                sender_id=handoff.source_agent_id,
                recipient_id=handoff.target_agent_id,
                task_data={
                    "handoff_id": handoff.handoff_id,
                    "task_type": handoff.task_type,
                    "task_data": handoff.task_data,
                    "priority": handoff.priority.value,
                    "deadline": handoff.deadline.isoformat() if handoff.deadline else None,
                    "context": handoff.context
                }
            )
            
            logger.info(f"Initiated task handoff {handoff.handoff_id}: {handoff.source_agent_id} -> {handoff.target_agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initiate task handoff {handoff.handoff_id}: {e}")
            return False
    
    async def start_workflow(self, workflow_type: str, participants: List[str], context: Dict[str, Any] = None) -> Optional[str]:
        """Start a new research workflow"""
        try:
            workflow_id = str(uuid4())
            
            if workflow_type not in self.workflow_handlers:
                logger.error(f"Unknown workflow type: {workflow_type}")
                return None
            
            # Verify all participants are available
            for agent_id in participants:
                agent = await self.agent_registry.get_agent(agent_id)
                if not agent:
                    logger.error(f"Participant agent {agent_id} not found")
                    return None
            
            # Create workflow
            workflow = ResearchWorkflow(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                participants=participants,
                status=WorkflowStatus.PENDING,
                current_step=0,
                total_steps=self._get_workflow_steps(workflow_type),
                context=context or {},
                results={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                coordinator_id=participants[0] if participants else None
            )
            
            self.active_workflows[workflow_id] = workflow
            
            # Start the workflow
            asyncio.create_task(self._execute_workflow(workflow))
            
            logger.info(f"Started workflow {workflow_id} ({workflow_type}) with {len(participants)} participants")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to start workflow {workflow_type}: {e}")
            return None
    
    async def _execute_workflow(self, workflow: ResearchWorkflow) -> None:
        """Execute a research workflow"""
        try:
            workflow.status = WorkflowStatus.RUNNING
            workflow.updated_at = datetime.utcnow()
            
            # Get the workflow handler
            handler = self.workflow_handlers[workflow.workflow_type]
            
            # Execute the workflow
            success = await handler(workflow)
            
            if success:
                workflow.status = WorkflowStatus.COMPLETED
                logger.info(f"Workflow {workflow.workflow_id} completed successfully")
            else:
                workflow.status = WorkflowStatus.FAILED
                logger.error(f"Workflow {workflow.workflow_id} failed")
            
            workflow.updated_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow.workflow_id}: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.updated_at = datetime.utcnow()
    
    def _get_workflow_steps(self, workflow_type: str) -> int:
        """Get the number of steps for a workflow type"""
        steps_map = {
            "hypothesis_to_experiment": 3,
            "experiment_to_analysis": 3,
            "full_research_cycle": 6,
            "literature_review": 4,
            "peer_review": 3
        }
        return steps_map.get(workflow_type, 1)
    
    # Workflow Handlers
    
    async def _handle_hypothesis_to_experiment(self, workflow: ResearchWorkflow) -> bool:
        """Handle hypothesis generation to experiment design workflow"""
        try:
            if len(workflow.participants) < 2:
                logger.error("Hypothesis-to-experiment workflow requires at least 2 agents")
                return False
            
            theory_agent = workflow.participants[0]
            experimental_agent = workflow.participants[1]
            
            # Step 1: Theory agent generates hypothesis
            workflow.current_step = 1
            hypothesis_handoff = TaskHandoff(
                handoff_id=str(uuid4()),
                source_agent_id="system",
                target_agent_id=theory_agent,
                task_type="generate_hypothesis",
                task_data=workflow.context,
                required_capabilities=[AgentCapability.HYPOTHESIS_GENERATION],
                priority=TaskPriority.NORMAL
            )
            
            await self.initiate_task_handoff(hypothesis_handoff)
            
            # Wait for hypothesis (simplified - in real implementation, use message handlers)
            await asyncio.sleep(2)  # Simulate processing time
            
            # Step 2: Hand off to experimental agent
            workflow.current_step = 2
            experiment_handoff = TaskHandoff(
                handoff_id=str(uuid4()),
                source_agent_id=theory_agent,
                target_agent_id=experimental_agent,
                task_type="design_experiment",
                task_data={"hypothesis": "Generated hypothesis", **workflow.context},
                required_capabilities=[AgentCapability.EXPERIMENTAL_DESIGN],
                priority=TaskPriority.NORMAL
            )
            
            await self.initiate_task_handoff(experiment_handoff)
            await asyncio.sleep(2)  # Simulate processing time
            
            # Step 3: Complete workflow
            workflow.current_step = 3
            workflow.results = {
                "hypothesis": "Generated hypothesis",
                "experiment_design": "Experimental protocol",
                "completion_time": datetime.utcnow().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error in hypothesis-to-experiment workflow: {e}")
            return False
    
    async def _handle_experiment_to_analysis(self, workflow: ResearchWorkflow) -> bool:
        """Handle experiment execution to data analysis workflow"""
        try:
            if len(workflow.participants) < 2:
                logger.error("Experiment-to-analysis workflow requires at least 2 agents")
                return False
            
            experimental_agent = workflow.participants[0]
            analysis_agent = workflow.participants[1]
            
            # Step 1: Execute experiment
            workflow.current_step = 1
            execution_handoff = TaskHandoff(
                handoff_id=str(uuid4()),
                source_agent_id="system",
                target_agent_id=experimental_agent,
                task_type="execute_experiment",
                task_data=workflow.context,
                required_capabilities=[AgentCapability.DATA_COLLECTION],
                priority=TaskPriority.HIGH
            )
            
            await self.initiate_task_handoff(execution_handoff)
            await asyncio.sleep(3)  # Simulate experiment execution
            
            # Step 2: Hand off data to analysis agent
            workflow.current_step = 2
            analysis_handoff = TaskHandoff(
                handoff_id=str(uuid4()),
                source_agent_id=experimental_agent,
                target_agent_id=analysis_agent,
                task_type="analyze_data",
                task_data={"experiment_data": "Raw experimental data", **workflow.context},
                required_capabilities=[AgentCapability.DATA_ANALYSIS],
                priority=TaskPriority.HIGH
            )
            
            await self.initiate_task_handoff(analysis_handoff)
            await asyncio.sleep(2)  # Simulate analysis
            
            # Step 3: Generate results
            workflow.current_step = 3
            workflow.results = {
                "raw_data": "Experimental data",
                "analysis_results": "Statistical analysis",
                "conclusions": "Data-driven conclusions",
                "completion_time": datetime.utcnow().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error in experiment-to-analysis workflow: {e}")
            return False
    
    async def _handle_full_research_cycle(self, workflow: ResearchWorkflow) -> bool:
        """Handle complete research cycle workflow"""
        try:
            if len(workflow.participants) < 3:
                logger.error("Full research cycle requires at least 3 agents")
                return False
            
            # This combines hypothesis-to-experiment and experiment-to-analysis
            # Step 1-3: Hypothesis to experiment
            sub_workflow1 = ResearchWorkflow(
                workflow_id=f"{workflow.workflow_id}_sub1",
                workflow_type="hypothesis_to_experiment",
                participants=workflow.participants[:2],
                status=WorkflowStatus.PENDING,
                current_step=0,
                total_steps=3,
                context=workflow.context,
                results={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            success1 = await self._handle_hypothesis_to_experiment(sub_workflow1)
            if not success1:
                return False
            
            workflow.current_step = 3
            
            # Step 4-6: Experiment to analysis
            sub_workflow2 = ResearchWorkflow(
                workflow_id=f"{workflow.workflow_id}_sub2",
                workflow_type="experiment_to_analysis",
                participants=workflow.participants[1:3],
                status=WorkflowStatus.PENDING,
                current_step=0,
                total_steps=3,
                context={**workflow.context, **sub_workflow1.results},
                results={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            success2 = await self._handle_experiment_to_analysis(sub_workflow2)
            if not success2:
                return False
            
            workflow.current_step = 6
            workflow.results = {
                **sub_workflow1.results,
                **sub_workflow2.results,
                "full_cycle_completion": datetime.utcnow().isoformat()
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error in full research cycle workflow: {e}")
            return False
    
    async def _handle_literature_review(self, workflow: ResearchWorkflow) -> bool:
        """Handle literature review workflow"""
        # Simplified implementation
        workflow.current_step = workflow.total_steps
        workflow.results = {"literature_summary": "Review completed"}
        return True
    
    async def _handle_peer_review(self, workflow: ResearchWorkflow) -> bool:
        """Handle peer review workflow"""
        # Simplified implementation
        workflow.current_step = workflow.total_steps
        workflow.results = {"review_score": 85, "feedback": "Well conducted research"}
        return True
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow.workflow_id,
            "workflow_type": workflow.workflow_type,
            "status": workflow.status.value,
            "current_step": workflow.current_step,
            "total_steps": workflow.total_steps,
            "progress": workflow.current_step / workflow.total_steps,
            "participants": workflow.participants,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "results": workflow.results if workflow.status == WorkflowStatus.COMPLETED else {}
        }
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False
        
        if workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            return False
        
        workflow.status = WorkflowStatus.CANCELLED
        workflow.updated_at = datetime.utcnow()
        
        logger.info(f"Cancelled workflow {workflow_id}")
        return True
    
    async def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows"""
        active_workflows = []
        
        for workflow_id, workflow in self.active_workflows.items():
            if workflow.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
                status = await self.get_workflow_status(workflow_id)
                if status:
                    active_workflows.append(status)
        
        return active_workflows 