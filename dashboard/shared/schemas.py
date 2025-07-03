"""
Shared Data Schemas for Dashboard API
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ComponentStatus(str, Enum):
    """Component health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class AgentStatus(str, Enum):
    """Agent status"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class TestStatus(str, Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ComponentInfo(BaseModel):
    """Information about a system component"""
    name: str
    status: ComponentStatus
    uptime_seconds: float
    last_heartbeat: datetime
    error_count: int = 0
    performance_score: float = 100.0


class PerformanceMetrics(BaseModel):
    """System performance metrics"""
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    active_tasks: int = 0
    queue_length: int = 0
    response_time_ms: float = 0.0


class SystemOverview(BaseModel):
    """Complete system status overview"""
    timestamp: datetime
    components: Dict[str, ComponentInfo]
    performance: PerformanceMetrics
    overall_health: ComponentStatus
    active_workflows: int = 0
    total_agents: int = 0


class WorkflowStartRequest(BaseModel):
    """Request to start a new workflow"""
    project_name: str
    research_topic: str
    workflow_template: str = "quick_validation"
    parameters: Dict[str, Any] = {}


class TestExecutionRequest(BaseModel):
    """Request to execute tests"""
    test_suite: str = "e2e_demo"
    test_scenarios: Optional[List[str]] = None
    parameters: Dict[str, Any] = {}


class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
