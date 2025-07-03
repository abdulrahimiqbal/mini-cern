"""
WebSocket Event Definitions for Dashboard Real-time Communication
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class EventType(str, Enum):
    """WebSocket event types for real-time updates"""
    
    # System status events
    SYSTEM_STATUS_UPDATE = "system_status_update"
    COMPONENT_STATUS_CHANGE = "component_status_change"
    PERFORMANCE_METRICS_UPDATE = "performance_metrics_update"
    
    # Workflow events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_PROGRESS_UPDATE = "workflow_progress_update"
    WORKFLOW_STEP_COMPLETED = "workflow_step_completed"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    WORKFLOW_STOPPED = "workflow_stopped"
    
    # Agent events
    AGENT_STATUS_CHANGE = "agent_status_change"
    AGENT_TASK_ASSIGNED = "agent_task_assigned"
    AGENT_TASK_COMPLETED = "agent_task_completed"
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    
    # Safety events
    SAFETY_VIOLATION_DETECTED = "safety_violation_detected"
    SAFETY_VIOLATION_RESOLVED = "safety_violation_resolved"
    SAFETY_STATUS_CHANGE = "safety_status_change"
    EMERGENCY_STOP_TRIGGERED = "emergency_stop_triggered"
    
    # Quality events
    QUALITY_REVIEW_STARTED = "quality_review_started"
    QUALITY_REVIEW_COMPLETED = "quality_review_completed"
    QUALITY_SCORE_UPDATE = "quality_score_update"
    
    # Testing events
    TEST_STARTED = "test_started"
    TEST_PROGRESS_UPDATE = "test_progress_update"
    TEST_COMPLETED = "test_completed"
    TEST_FAILED = "test_failed"
    TEST_SUITE_STARTED = "test_suite_started"
    TEST_SUITE_COMPLETED = "test_suite_completed"
    
    # Task events
    TASK_CREATED = "task_created"
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    
    # Connection events
    CLIENT_CONNECTED = "client_connected"
    CLIENT_DISCONNECTED = "client_disconnected"
    HEARTBEAT = "heartbeat"


class DashboardEvent(BaseModel):
    """Base dashboard event model"""
    
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    event_id: Optional[str] = None
    source_component: Optional[str] = None
    priority: Optional[int] = 1  # 1=low, 2=medium, 3=high, 4=critical


def create_system_status_event(
    components_status: Dict[str, Any],
    performance_metrics: Dict[str, Any]
) -> DashboardEvent:
    """Create system status update event"""
    return DashboardEvent(
        event_type=EventType.SYSTEM_STATUS_UPDATE,
        timestamp=datetime.now(),
        data={
            "components": components_status,
            "performance": performance_metrics
        },
        source_component="system_monitor"
    )


def create_workflow_progress_event(
    cycle_id: str,
    project_id: str,
    current_step: str,
    progress_percentage: float,
    steps_status: List[Dict[str, Any]]
) -> DashboardEvent:
    """Create workflow progress update event"""
    return DashboardEvent(
        event_type=EventType.WORKFLOW_PROGRESS_UPDATE,
        timestamp=datetime.now(),
        data={
            "cycle_id": cycle_id,
            "project_id": project_id,
            "current_step": current_step,
            "progress_percentage": progress_percentage,
            "steps_status": steps_status
        },
        source_component="workflow_engine"
    )


def create_test_progress_event(
    test_id: str,
    test_name: str,
    progress_percentage: float,
    current_phase: str,
    results: Optional[Dict[str, Any]] = None
) -> DashboardEvent:
    """Create test progress update event"""
    return DashboardEvent(
        event_type=EventType.TEST_PROGRESS_UPDATE,
        timestamp=datetime.now(),
        data={
            "test_id": test_id,
            "test_name": test_name,
            "progress_percentage": progress_percentage,
            "current_phase": current_phase,
            "results": results or {}
        },
        source_component="test_runner"
    )
