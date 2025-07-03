"""
Research Orchestrator - Central Control Engine
Manages the lifecycle and coordination of all research projects
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from .research_project import ResearchProject, ResearchState, Priority

logger = logging.getLogger(__name__)

class ResearchOrchestrator:
    """
    Central orchestration engine for autonomous research projects
    
    This is the brain of the system that:
    - Manages multiple concurrent research projects
    - Coordinates agent assignments
    - Handles project lifecycle transitions
    - Monitors system resources and constraints
    - Provides real-time project status
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", max_concurrent_projects: int = 5):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        
        # Project management
        self.active_projects: Dict[str, ResearchProject] = {}
        self.project_queue: List[str] = []  # Queue of project IDs waiting to start
        
        # System constraints
        self.max_concurrent_projects = max_concurrent_projects
        self.total_budget_limit = 50000.0  # USD
        self.current_budget_used = 0.0
        
        # Agent management
        self.available_agents: Set[str] = set()
        self.agent_assignments: Dict[str, str] = {}  # agent_id -> project_id
        
        # System state
        self.is_running = False
        self.stats = {
            "projects_created": 0,
            "projects_completed": 0,
            "projects_failed": 0,
            "total_compute_hours": 0.0,
            "uptime_hours": 0.0
        }
        
        # Event handlers
        self.event_handlers: Dict[str, List[callable]] = {
            "project_created": [],
            "project_started": [],
            "project_completed": [],
            "project_failed": [],
            "agent_assigned": [],
            "budget_warning": []
        }
    
    async def initialize(self) -> None:
        """Initialize the orchestrator and connect to Redis"""
        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
            
            # Load existing projects from Redis
            await self._load_projects_from_storage()
            
            # Register default agents (we'll expand this in later phases)
            self.available_agents = {"theory_agent", "experimental_agent", "analysis_agent"}
            
            self.is_running = True
            logger.info(f"Research Orchestrator initialized with {len(self.active_projects)} active projects")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the orchestrator"""
        self.is_running = False
        
        # Save all projects to storage
        await self._save_all_projects()
        
        if self.redis:
            await self.redis.close()
        
        logger.info("Research Orchestrator shutdown complete")
    
    async def create_project(
        self,
        title: str,
        research_question: str,
        physics_domain: str = "general",
        priority: Priority = Priority.MEDIUM,
        max_cost_usd: float = 1000.0,
        expected_duration_hours: int = 24
    ) -> ResearchProject:
        """Create a new research project"""
        
        # Validate budget
        if self.current_budget_used + max_cost_usd > self.total_budget_limit:
            raise ValueError(f"Project would exceed budget limit. Available: ${self.total_budget_limit - self.current_budget_used}")
        
        # Create project
        project = ResearchProject(
            title=title,
            research_question=research_question,
            physics_domain=physics_domain,
            priority=priority,
            max_cost_usd=max_cost_usd,
            expected_duration_hours=expected_duration_hours
        )
        
        # Add to queue or start immediately
        if len(self.get_active_projects()) < self.max_concurrent_projects:
            await self._start_project(project)
        else:
            self.project_queue.append(project.id)
            logger.info(f"Project {project.id} queued (system at capacity)")
        
        # Store in memory and Redis
        self.active_projects[project.id] = project
        await self._save_project(project)
        
        # Update stats
        self.stats["projects_created"] += 1
        
        # Trigger events
        await self._trigger_event("project_created", project)
        
        logger.info(f"Created project: {project.title} (ID: {project.id})")
        return project
    
    async def _start_project(self, project: ResearchProject) -> None:
        """Start executing a research project"""
        project.update_state(ResearchState.PLANNING, "Project started by orchestrator")
        
        # Auto-assign agents based on project type
        await self._assign_optimal_agents(project)
        
        # Update budget tracking
        self.current_budget_used += project.max_cost_usd
        
        await self._trigger_event("project_started", project)
        logger.info(f"Started project: {project.title}")
    
    async def _assign_optimal_agents(self, project: ResearchProject) -> None:
        """Assign the best available agents to a project"""
        
        # Simple assignment logic (we'll make this smarter in later phases)
        available = self.available_agents - set(self.agent_assignments.keys())
        
        if not available:
            logger.warning(f"No agents available for project {project.id}")
            return
        
        # Assign primary agent based on physics domain
        primary_agent = None
        if project.physics_domain in ["optics", "quantum"]:
            primary_agent = "theory_agent" if "theory_agent" in available else None
        else:
            primary_agent = "experimental_agent" if "experimental_agent" in available else None
        
        if not primary_agent:
            primary_agent = next(iter(available))
        
        # Assign agents
        project.assign_agent(primary_agent, "primary")
        self.agent_assignments[primary_agent] = project.id
        
        # Assign additional agents if available
        remaining = available - {primary_agent}
        for agent_id in list(remaining)[:2]:  # Assign up to 2 additional agents
            project.assign_agent(agent_id, "collaborator")
            self.agent_assignments[agent_id] = project.id
        
        await self._trigger_event("agent_assigned", {"project": project, "agents": project.assigned_agents})
        logger.info(f"Assigned agents {project.assigned_agents} to project {project.id}")
    
    async def update_project_progress(self, project_id: str, progress: float, note: str = "") -> None:
        """Update project progress and handle state transitions"""
        project = self.active_projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        project.update_progress(progress, note)
        
        # Auto-transition states based on progress
        if progress >= 100.0 and project.state != ResearchState.COMPLETED:
            await self.complete_project(project_id, "Automatic completion - 100% progress reached")
        elif progress >= 80.0 and project.state == ResearchState.EXECUTING:
            project.update_state(ResearchState.ANALYZING, "Moving to analysis phase")
        
        await self._save_project(project)
    
    async def complete_project(self, project_id: str, note: str = "") -> None:
        """Mark a project as completed and free up resources"""
        project = self.active_projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        project.update_state(ResearchState.COMPLETED, note)
        
        # Free up agents
        for agent_id in project.assigned_agents:
            self.agent_assignments.pop(agent_id, None)
        
        # Update budget (could add cost tracking here)
        self.current_budget_used -= project.max_cost_usd
        
        # Update stats
        self.stats["projects_completed"] += 1
        if project.get_duration():
            self.stats["total_compute_hours"] += project.get_duration()
        
        # Start next project in queue
        await self._start_next_queued_project()
        
        await self._trigger_event("project_completed", project)
        logger.info(f"Completed project: {project.title}")
    
    async def fail_project(self, project_id: str, reason: str) -> None:
        """Mark a project as failed and free up resources"""
        project = self.active_projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        project.update_state(ResearchState.FAILED, f"Project failed: {reason}")
        
        # Free up agents
        for agent_id in project.assigned_agents:
            self.agent_assignments.pop(agent_id, None)
        
        # Update budget
        self.current_budget_used -= project.max_cost_usd
        
        # Update stats
        self.stats["projects_failed"] += 1
        
        # Start next project in queue
        await self._start_next_queued_project()
        
        await self._trigger_event("project_failed", project)
        logger.error(f"Failed project: {project.title} - {reason}")
    
    async def _start_next_queued_project(self) -> None:
        """Start the next project in the queue if capacity allows"""
        if not self.project_queue:
            return
        
        if len(self.get_active_projects()) >= self.max_concurrent_projects:
            return
        
        project_id = self.project_queue.pop(0)
        project = self.active_projects.get(project_id)
        
        if project and project.state == ResearchState.INITIAL:
            await self._start_project(project)
    
    def get_active_projects(self) -> List[ResearchProject]:
        """Get all currently active projects"""
        return [p for p in self.active_projects.values() if p.is_active()]
    
    def get_project(self, project_id: str) -> Optional[ResearchProject]:
        """Get a specific project by ID"""
        return self.active_projects.get(project_id)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        active_projects = self.get_active_projects()
        
        return {
            "is_running": self.is_running,
            "timestamp": datetime.utcnow().isoformat(),
            "projects": {
                "total": len(self.active_projects),
                "active": len(active_projects),
                "queued": len(self.project_queue),
                "max_concurrent": self.max_concurrent_projects
            },
            "agents": {
                "total": len(self.available_agents),
                "assigned": len(self.agent_assignments),
                "available": len(self.available_agents) - len(self.agent_assignments)
            },
            "budget": {
                "limit": self.total_budget_limit,
                "used": self.current_budget_used,
                "remaining": self.total_budget_limit - self.current_budget_used,
                "utilization_percent": (self.current_budget_used / self.total_budget_limit) * 100
            },
            "stats": self.stats
        }
    
    async def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register an event handler for system events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _trigger_event(self, event_type: str, data: Any) -> None:
        """Trigger all handlers for a specific event type"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    async def _save_project(self, project: ResearchProject) -> None:
        """Save a project to Redis storage"""
        if not self.redis:
            return
        
        try:
            await self.redis.set(
                f"project:{project.id}",
                json.dumps(project.to_dict()),
                ex=86400 * 30  # Expire after 30 days
            )
        except Exception as e:
            logger.error(f"Failed to save project {project.id}: {e}")
    
    async def _save_all_projects(self) -> None:
        """Save all projects to storage"""
        for project in self.active_projects.values():
            await self._save_project(project)
    
    async def _load_projects_from_storage(self) -> None:
        """Load existing projects from Redis storage"""
        if not self.redis:
            return
        
        try:
            keys = await self.redis.keys("project:*")
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    project_dict = json.loads(data)
                    project = ResearchProject.from_dict(project_dict)
                    self.active_projects[project.id] = project
            
            logger.info(f"Loaded {len(self.active_projects)} projects from storage")
            
        except Exception as e:
            logger.error(f"Failed to load projects from storage: {e}")
    
    async def run_maintenance(self) -> None:
        """Run periodic maintenance tasks"""
        logger.info("Running orchestrator maintenance...")
        
        # Check for stale projects
        current_time = datetime.utcnow()
        for project in list(self.active_projects.values()):
            if project.is_active():
                # Check if project has been running too long
                if project.started_at:
                    runtime = current_time - project.started_at
                    max_runtime = timedelta(hours=project.expected_duration_hours * 2)  # 2x safety margin
                    
                    if runtime > max_runtime:
                        await self.fail_project(
                            project.id,
                            f"Project exceeded maximum runtime ({runtime.total_seconds() / 3600:.1f} hours)"
                        )
        
        # Budget warning
        budget_utilization = (self.current_budget_used / self.total_budget_limit) * 100
        if budget_utilization > 80.0:
            await self._trigger_event("budget_warning", {
                "utilization_percent": budget_utilization,
                "remaining_budget": self.total_budget_limit - self.current_budget_used
            })
        
        # Save all projects
        await self._save_all_projects()
        
        logger.info("Maintenance complete") 