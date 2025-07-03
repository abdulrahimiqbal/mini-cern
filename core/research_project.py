"""
Research Project Core Module
Manages the state and lifecycle of autonomous research projects
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import uuid
from datetime import datetime
import json

class ResearchState(Enum):
    """Research project lifecycle states"""
    INITIAL = "initial"
    PLANNING = "planning"
    DESIGNING = "designing"
    EXECUTING = "executing"
    ANALYZING = "analyzing"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class Priority(Enum):
    """Research priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ResearchMetrics:
    """Metrics for tracking research progress"""
    progress_percentage: float = 0.0
    experiments_completed: int = 0
    data_points_collected: int = 0
    hypotheses_tested: int = 0
    compute_hours_used: float = 0.0
    cost_usd: float = 0.0

@dataclass
class ResearchProject:
    """
    Core research project representation
    Manages the complete lifecycle of an autonomous research investigation
    """
    
    # Core Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    research_question: str = ""
    hypothesis: str = ""
    
    # State Management
    state: ResearchState = ResearchState.INITIAL
    priority: Priority = Priority.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Research Configuration
    physics_domain: str = "general"  # optics, quantum, mechanics, etc.
    expected_duration_hours: int = 24
    max_cost_usd: float = 1000.0
    
    # Agent Assignments
    assigned_agents: List[str] = field(default_factory=list)
    primary_agent: Optional[str] = None
    
    # Results and Data
    results: Dict[str, Any] = field(default_factory=dict)
    datasets: List[str] = field(default_factory=list)
    publications: List[str] = field(default_factory=list)
    
    # Metrics
    metrics: ResearchMetrics = field(default_factory=ResearchMetrics)
    
    # System Data
    metadata: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_state(self, new_state: ResearchState, note: str = "") -> None:
        """Update project state with automatic timestamp tracking"""
        old_state = self.state
        self.state = new_state
        self.updated_at = datetime.utcnow()
        
        # Special timestamp tracking
        if new_state == ResearchState.EXECUTING and not self.started_at:
            self.started_at = datetime.utcnow()
        elif new_state in [ResearchState.COMPLETED, ResearchState.FAILED]:
            self.completed_at = datetime.utcnow()
            
        # Log the state change
        self.add_log(
            event_type="state_change",
            data={
                "old_state": old_state.value,
                "new_state": new_state.value,
                "note": note
            }
        )
    
    def add_log(self, event_type: str, data: Dict[str, Any]) -> None:
        """Add a timestamped log entry"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.logs.append(log_entry)
        
        # Keep only last 1000 log entries to prevent memory bloat
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
    
    def assign_agent(self, agent_id: str, role: str = "collaborator") -> None:
        """Assign an agent to this research project"""
        if agent_id not in self.assigned_agents:
            self.assigned_agents.append(agent_id)
            
        if role == "primary":
            self.primary_agent = agent_id
            
        self.add_log(
            event_type="agent_assigned",
            data={"agent_id": agent_id, "role": role}
        )
    
    def update_progress(self, percentage: float, note: str = "") -> None:
        """Update research progress percentage"""
        self.metrics.progress_percentage = max(0.0, min(100.0, percentage))
        self.updated_at = datetime.utcnow()
        
        self.add_log(
            event_type="progress_update",
            data={"progress": percentage, "note": note}
        )
    
    def add_result(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> None:
        """Add a research result"""
        self.results[key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.add_log(
            event_type="result_added",
            data={"key": key, "result_type": type(value).__name__}
        )
    
    def get_duration(self) -> Optional[float]:
        """Get project duration in hours"""
        if not self.started_at:
            return None
            
        end_time = self.completed_at or datetime.utcnow()
        duration = end_time - self.started_at
        return duration.total_seconds() / 3600
    
    def is_active(self) -> bool:
        """Check if project is in an active state"""
        return self.state in [
            ResearchState.PLANNING,
            ResearchState.DESIGNING,
            ResearchState.EXECUTING,
            ResearchState.ANALYZING
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "research_question": self.research_question,
            "hypothesis": self.hypothesis,
            "state": self.state.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "physics_domain": self.physics_domain,
            "expected_duration_hours": self.expected_duration_hours,
            "max_cost_usd": self.max_cost_usd,
            "assigned_agents": self.assigned_agents,
            "primary_agent": self.primary_agent,
            "results": self.results,
            "datasets": self.datasets,
            "publications": self.publications,
            "metrics": {
                "progress_percentage": self.metrics.progress_percentage,
                "experiments_completed": self.metrics.experiments_completed,
                "data_points_collected": self.metrics.data_points_collected,
                "hypotheses_tested": self.metrics.hypotheses_tested,
                "compute_hours_used": self.metrics.compute_hours_used,
                "cost_usd": self.metrics.cost_usd
            },
            "metadata": self.metadata,
            "logs": self.logs[-10:]  # Only include last 10 logs in serialization
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchProject':
        """Create project from dictionary"""
        # Parse timestamps
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])
        started_at = datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None
        completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        
        # Create metrics object
        metrics_data = data.get("metrics", {})
        metrics = ResearchMetrics(
            progress_percentage=metrics_data.get("progress_percentage", 0.0),
            experiments_completed=metrics_data.get("experiments_completed", 0),
            data_points_collected=metrics_data.get("data_points_collected", 0),
            hypotheses_tested=metrics_data.get("hypotheses_tested", 0),
            compute_hours_used=metrics_data.get("compute_hours_used", 0.0),
            cost_usd=metrics_data.get("cost_usd", 0.0)
        )
        
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            research_question=data["research_question"],
            hypothesis=data["hypothesis"],
            state=ResearchState(data["state"]),
            priority=Priority(data["priority"]),
            created_at=created_at,
            updated_at=updated_at,
            started_at=started_at,
            completed_at=completed_at,
            physics_domain=data["physics_domain"],
            expected_duration_hours=data["expected_duration_hours"],
            max_cost_usd=data["max_cost_usd"],
            assigned_agents=data["assigned_agents"],
            primary_agent=data.get("primary_agent"),
            results=data.get("results", {}),
            datasets=data.get("datasets", []),
            publications=data.get("publications", []),
            metrics=metrics,
            metadata=data.get("metadata", {}),
            logs=data.get("logs", [])
        ) 