"""
Task Scheduler - Advanced Priority and Resource Management
Handles intelligent task scheduling and resource allocation for research workflows
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
import heapq
from collections import defaultdict

from communication.agent_registry import AgentRegistry, RegistrationStatus
from agents.agent_types import AgentType, AgentCapability
from workflow.workflow_engine import WorkflowState, AutomatedResearchCycle

logger = logging.getLogger(__name__)

class PriorityLevel(Enum):
    """Task priority levels with numeric values for scheduling"""
    CRITICAL = 0    # Highest priority
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4  # Lowest priority

class TaskStatus(Enum):
    """Status of scheduled tasks"""
    QUEUED = "queued"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class ResourceType(Enum):
    """Types of resources that can be allocated"""
    AGENT = "agent"
    COMPUTE = "compute"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"

@dataclass
class ResourceRequirement:
    """Specification of required resources for a task"""
    resource_type: ResourceType
    amount: float
    unit: str
    max_wait_time_minutes: int = 30

@dataclass
class ResourceAllocation:
    """Allocated resources for a task"""
    allocation_id: str
    task_id: str
    resource_type: ResourceType
    allocated_amount: float
    allocated_resources: List[str]  # IDs of allocated resources
    allocated_at: datetime
    expires_at: Optional[datetime] = None

@dataclass
class ScheduledTask:
    """Task in the scheduling system"""
    task_id: str
    task_type: str
    priority: PriorityLevel
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Task definition
    workflow_step_id: Optional[str] = None
    cycle_id: Optional[str] = None
    agent_requirements: List[AgentType] = field(default_factory=list)
    capability_requirements: List[AgentCapability] = field(default_factory=list)
    resource_requirements: List[ResourceRequirement] = field(default_factory=list)
    
    # Execution tracking
    status: TaskStatus = TaskStatus.QUEUED
    assigned_agent_id: Optional[str] = None
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Task IDs
    blocks: List[str] = field(default_factory=list)      # Task IDs that depend on this
    
    # Execution data
    task_data: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Retry configuration
    max_retries: int = 3
    retry_count: int = 0
    retry_delay_minutes: int = 5
    
    def __lt__(self, other):
        """For priority queue ordering"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at

class TaskScheduler:
    """
    Advanced Task Scheduler for Research Workflows
    
    Provides intelligent scheduling with:
    - Priority-based task queuing
    - Resource allocation and management
    - Load balancing across agents
    - Deadline awareness
    - Dependency management
    """
    
    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
        
        # Task management
        self.task_queue: List[ScheduledTask] = []  # Priority queue
        self.active_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: Dict[str, ScheduledTask] = {}
        
        # Resource management
        self.resource_allocations: Dict[str, ResourceAllocation] = {}
        self.agent_workloads: Dict[str, int] = defaultdict(int)
        self.resource_limits: Dict[ResourceType, float] = {
            ResourceType.AGENT: 100,      # Max 100 concurrent agent tasks
            ResourceType.COMPUTE: 1000,   # Arbitrary compute units
            ResourceType.MEMORY: 16384,   # MB
            ResourceType.STORAGE: 102400, # MB
            ResourceType.NETWORK: 1000    # Arbitrary network units
        }
        self.resource_usage: Dict[ResourceType, float] = defaultdict(float)
        
        # Scheduling configuration
        self.max_concurrent_tasks = 50
        self.scheduling_interval_seconds = 10
        self.cleanup_interval_hours = 24
        
        # Statistics
        self.stats = {
            "tasks_scheduled": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_wait_time_minutes": 0.0,
            "average_execution_time_minutes": 0.0,
            "resource_utilization": {}
        }
        
        # Background tasks
        self.is_running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the task scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduling_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Task scheduler started")
    
    async def stop(self) -> None:
        """Stop the task scheduler"""
        self.is_running = False
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        logger.info("Task scheduler stopped")
    
    async def schedule_task(self, task: ScheduledTask) -> bool:
        """Schedule a new task"""
        try:
            # Validate task
            if not await self._validate_task(task):
                logger.error(f"Task validation failed for {task.task_id}")
                return False
            
            # Add to queue
            heapq.heappush(self.task_queue, task)
            self.stats["tasks_scheduled"] += 1
            
            logger.info(f"Scheduled task {task.task_id} with priority {task.priority.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule task {task.task_id}: {e}")
            return False
    
    async def schedule_workflow_step(self, cycle: AutomatedResearchCycle, 
                                   step_index: int, priority: PriorityLevel = PriorityLevel.MEDIUM) -> Optional[str]:
        """Schedule a workflow step as a task"""
        try:
            if step_index >= len(cycle.template.steps):
                return None
            
            step = cycle.template.steps[step_index]
            task_id = f"{cycle.cycle_id}_{step.step_id}"
            
            # Create scheduled task
            task = ScheduledTask(
                task_id=task_id,
                task_type="workflow_step",
                priority=priority,
                created_at=datetime.utcnow(),
                workflow_step_id=step.step_id,
                cycle_id=cycle.cycle_id,
                agent_requirements=[step.required_agent_type],
                capability_requirements=step.required_capabilities,
                task_data={
                    "step_definition": step.__dict__,
                    "cycle_context": cycle.__dict__
                },
                max_retries=2
            )
            
            # Set deadline based on step duration
            if step.estimated_duration_minutes > 0:
                task.deadline = datetime.utcnow() + timedelta(minutes=step.estimated_duration_minutes * 2)
            
            # Add dependencies
            for dep_step_id in step.dependencies:
                dep_task_id = f"{cycle.cycle_id}_{dep_step_id}"
                task.depends_on.append(dep_task_id)
            
            success = await self.schedule_task(task)
            return task_id if success else None
            
        except Exception as e:
            logger.error(f"Failed to schedule workflow step: {e}")
            return None
    
    async def _validate_task(self, task: ScheduledTask) -> bool:
        """Validate a task before scheduling"""
        # Check if agents are available for requirements
        if task.agent_requirements:
            for agent_type in task.agent_requirements:
                available_agents = await self.agent_registry.get_agents_by_type(agent_type)
                if not available_agents:
                    logger.warning(f"No agents available for type {agent_type}")
                    return False
        
        # Check resource requirements
        for req in task.resource_requirements:
            if req.resource_type in self.resource_limits:
                limit = self.resource_limits[req.resource_type]
                current_usage = self.resource_usage[req.resource_type]
                if current_usage + req.amount > limit:
                    logger.warning(f"Insufficient {req.resource_type.value} resources")
                    return False
        
        return True
    
    async def _scheduling_loop(self) -> None:
        """Main scheduling loop"""
        while self.is_running:
            try:
                await self._process_task_queue()
                await asyncio.sleep(self.scheduling_interval_seconds)
            except Exception as e:
                logger.error(f"Error in scheduling loop: {e}")
                await asyncio.sleep(5)
    
    async def _process_task_queue(self) -> None:
        """Process tasks in the priority queue"""
        # Check for tasks ready to be scheduled
        ready_tasks = []
        
        while self.task_queue and len(self.active_tasks) < self.max_concurrent_tasks:
            task = heapq.heappop(self.task_queue)
            
            # Check if dependencies are satisfied
            if await self._check_dependencies(task):
                ready_tasks.append(task)
            else:
                # Put back in queue if dependencies not ready
                heapq.heappush(self.task_queue, task)
                break
        
        # Execute ready tasks
        for task in ready_tasks:
            await self._execute_task(task)
    
    async def _check_dependencies(self, task: ScheduledTask) -> bool:
        """Check if all task dependencies are satisfied"""
        for dep_task_id in task.depends_on:
            # Check if dependency is completed
            if dep_task_id not in self.completed_tasks:
                # Check if it's in active tasks
                if dep_task_id in self.active_tasks:
                    dep_task = self.active_tasks[dep_task_id]
                    if dep_task.status != TaskStatus.COMPLETED:
                        return False
                else:
                    return False
        
        return True
    
    async def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a scheduled task"""
        try:
            # Allocate resources
            allocation_success = await self._allocate_resources(task)
            if not allocation_success:
                # Requeue task if resources not available
                heapq.heappush(self.task_queue, task)
                return
            
            # Move to active tasks
            self.active_tasks[task.task_id] = task
            task.status = TaskStatus.ASSIGNED
            task.assigned_at = datetime.utcnow()
            
            # Start execution
            asyncio.create_task(self._run_task(task))
            
        except Exception as e:
            logger.error(f"Failed to execute task {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            await self._complete_task(task)
    
    async def _allocate_resources(self, task: ScheduledTask) -> bool:
        """Allocate required resources for a task"""
        allocations = []
        
        try:
            # Allocate agents
            if task.agent_requirements or task.capability_requirements:
                agent_id = await self._allocate_agent(task)
                if not agent_id:
                    return False
                
                task.assigned_agent_id = agent_id
                self.agent_workloads[agent_id] += 1
                
                allocation = ResourceAllocation(
                    allocation_id=str(uuid4()),
                    task_id=task.task_id,
                    resource_type=ResourceType.AGENT,
                    allocated_amount=1,
                    allocated_resources=[agent_id],
                    allocated_at=datetime.utcnow(),
                    expires_at=task.deadline
                )
                allocations.append(allocation)
            
            # Allocate other resources
            for req in task.resource_requirements:
                if req.resource_type != ResourceType.AGENT:
                    allocation = await self._allocate_resource(req, task.task_id)
                    if not allocation:
                        # Rollback previous allocations
                        for alloc in allocations:
                            await self._deallocate_resource(alloc)
                        return False
                    allocations.append(allocation)
            
            # Store allocations
            for allocation in allocations:
                self.resource_allocations[allocation.allocation_id] = allocation
            
            return True
            
        except Exception as e:
            logger.error(f"Resource allocation failed for task {task.task_id}: {e}")
            return False
    
    async def _allocate_agent(self, task: ScheduledTask) -> Optional[str]:
        """Allocate the best available agent for a task"""
        try:
            # Get candidate agents
            candidates = []
            
            if task.capability_requirements:
                for capability in task.capability_requirements:
                    agents = await self.agent_registry.find_agents_by_capability([capability])
                    candidates.extend(agents)
            
            if task.agent_requirements:
                for agent_type in task.agent_requirements:
                    agents = await self.agent_registry.get_agents_by_type(agent_type)
                    candidates.extend(agents)
            
            if not candidates:
                return None
            
            # Remove duplicates and filter by availability
            unique_candidates = {}
            for agent in candidates:
                agent_id = agent["agent_id"]
                if agent_id not in unique_candidates and agent["status"] == RegistrationStatus.ACTIVE.value:
                    unique_candidates[agent_id] = agent
            
            # Select best agent based on workload
            best_agent_id = None
            min_workload = float('inf')
            
            for agent_id, agent_info in unique_candidates.items():
                current_workload = self.agent_workloads[agent_id]
                
                # Consider agent reputation and capabilities
                reputation_score = agent_info.get("reputation_score", 50)
                capability_match = len(set(task.capability_requirements) & set(agent_info.get("capabilities", [])))
                
                # Calculate selection score (lower is better)
                score = current_workload - (reputation_score / 100) - (capability_match * 0.1)
                
                if score < min_workload:
                    min_workload = score
                    best_agent_id = agent_id
            
            return best_agent_id
            
        except Exception as e:
            logger.error(f"Agent allocation failed: {e}")
            return None
    
    async def _allocate_resource(self, requirement: ResourceRequirement, task_id: str) -> Optional[ResourceAllocation]:
        """Allocate a specific resource"""
        resource_type = requirement.resource_type
        
        # Check availability
        current_usage = self.resource_usage[resource_type]
        limit = self.resource_limits[resource_type]
        
        if current_usage + requirement.amount > limit:
            return None
        
        # Allocate resource
        self.resource_usage[resource_type] += requirement.amount
        
        allocation = ResourceAllocation(
            allocation_id=str(uuid4()),
            task_id=task_id,
            resource_type=resource_type,
            allocated_amount=requirement.amount,
            allocated_resources=[f"{resource_type.value}_{uuid4()}"],
            allocated_at=datetime.utcnow()
        )
        
        return allocation
    
    async def _run_task(self, task: ScheduledTask) -> None:
        """Run a task to completion"""
        try:
            task.status = TaskStatus.EXECUTING
            task.started_at = datetime.utcnow()
            
            # Simulate task execution (in real implementation, would delegate to agents)
            if task.task_type == "workflow_step":
                await self._execute_workflow_step_task(task)
            else:
                await self._execute_generic_task(task)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            self.stats["tasks_completed"] += 1
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            self.stats["tasks_failed"] += 1
            
            logger.error(f"Task {task.task_id} failed: {e}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.QUEUED
                task.scheduled_for = datetime.utcnow() + timedelta(minutes=task.retry_delay_minutes)
                heapq.heappush(self.task_queue, task)
                logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count + 1})")
                return
        
        finally:
            await self._complete_task(task)
    
    async def _execute_workflow_step_task(self, task: ScheduledTask) -> None:
        """Execute a workflow step task"""
        # Simulate workflow step execution
        step_data = task.task_data.get("step_definition", {})
        duration = step_data.get("estimated_duration_minutes", 5)
        
        # Simulate work
        await asyncio.sleep(min(duration, 10))  # Cap simulation time
        
        # Generate mock results
        task.results = {
            "step_completed": True,
            "execution_time_minutes": duration,
            "agent_used": task.assigned_agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_generic_task(self, task: ScheduledTask) -> None:
        """Execute a generic task"""
        # Simulate generic task execution
        await asyncio.sleep(2)
        
        task.results = {
            "task_completed": True,
            "execution_time": 2,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _complete_task(self, task: ScheduledTask) -> None:
        """Complete a task and clean up resources"""
        # Remove from active tasks
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        
        # Move to completed tasks
        self.completed_tasks[task.task_id] = task
        
        # Deallocate resources
        await self._deallocate_task_resources(task)
        
        # Update statistics
        if task.started_at and task.completed_at:
            execution_time = (task.completed_at - task.started_at).total_seconds() / 60
            self._update_stats("execution_time", execution_time)
        
        if task.assigned_at and task.started_at:
            wait_time = (task.started_at - task.assigned_at).total_seconds() / 60
            self._update_stats("wait_time", wait_time)
    
    async def _deallocate_task_resources(self, task: ScheduledTask) -> None:
        """Deallocate all resources for a task"""
        # Find allocations for this task
        to_remove = []
        for allocation_id, allocation in self.resource_allocations.items():
            if allocation.task_id == task.task_id:
                await self._deallocate_resource(allocation)
                to_remove.append(allocation_id)
        
        # Remove allocations
        for allocation_id in to_remove:
            del self.resource_allocations[allocation_id]
    
    async def _deallocate_resource(self, allocation: ResourceAllocation) -> None:
        """Deallocate a specific resource"""
        if allocation.resource_type == ResourceType.AGENT:
            for agent_id in allocation.allocated_resources:
                self.agent_workloads[agent_id] -= 1
                if self.agent_workloads[agent_id] <= 0:
                    del self.agent_workloads[agent_id]
        else:
            self.resource_usage[allocation.resource_type] -= allocation.allocated_amount
    
    def _update_stats(self, metric: str, value: float) -> None:
        """Update running statistics"""
        if metric == "execution_time":
            current_avg = self.stats["average_execution_time_minutes"]
            completed = self.stats["tasks_completed"]
            self.stats["average_execution_time_minutes"] = (current_avg * (completed - 1) + value) / completed
        
        elif metric == "wait_time":
            current_avg = self.stats["average_wait_time_minutes"]
            completed = self.stats["tasks_completed"]
            self.stats["average_wait_time_minutes"] = (current_avg * (completed - 1) + value) / completed
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup of old completed tasks"""
        while self.is_running:
            try:
                await self._cleanup_old_tasks()
                await asyncio.sleep(self.cleanup_interval_hours * 3600)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)  # Wait an hour on error
    
    async def _cleanup_old_tasks(self) -> None:
        """Remove old completed tasks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.cleanup_interval_hours)
        to_remove = []
        
        for task_id, task in self.completed_tasks.items():
            if task.completed_at and task.completed_at < cutoff_time:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.completed_tasks[task_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old tasks")
    
    async def cancel_task(self, task_id: str, reason: str = "") -> bool:
        """Cancel a scheduled or active task"""
        # Check queued tasks
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                task.status = TaskStatus.CANCELLED
                task.error_message = f"Cancelled: {reason}"
                del self.task_queue[i]
                heapq.heapify(self.task_queue)
                return True
        
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            task.error_message = f"Cancelled: {reason}"
            await self._complete_task(task)
            return True
        
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
        # Check completed tasks
        elif task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
        # Check queued tasks
        else:
            task = None
            for queued_task in self.task_queue:
                if queued_task.task_id == task_id:
                    task = queued_task
                    break
        
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status.value,
            "priority": task.priority.name,
            "created_at": task.created_at.isoformat(),
            "assigned_at": task.assigned_at.isoformat() if task.assigned_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "assigned_agent_id": task.assigned_agent_id,
            "retry_count": task.retry_count,
            "error_message": task.error_message,
            "results": task.results
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall scheduler system status"""
        # Calculate resource utilization
        resource_utilization = {}
        for resource_type, limit in self.resource_limits.items():
            usage = self.resource_usage[resource_type]
            utilization = (usage / limit) * 100 if limit > 0 else 0
            resource_utilization[resource_type.value] = {
                "usage": usage,
                "limit": limit,
                "utilization_percent": utilization
            }
        
        return {
            "scheduler_status": "running" if self.is_running else "stopped",
            "queued_tasks": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "active_agents": len(self.agent_workloads),
            "resource_utilization": resource_utilization,
            "statistics": self.stats
        } 