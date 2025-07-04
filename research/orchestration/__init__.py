"""
Research Orchestration Module
Handles intelligent task decomposition and multi-agent coordination
"""

from .orchestrator import ResearchOrchestrator, ResearchProject, ResearchTask
from .task_manager import TaskManager
from .agent_coordinator import AgentCoordinator

__all__ = [
    "ResearchOrchestrator",
    "ResearchProject", 
    "ResearchTask",
    "TaskManager",
    "AgentCoordinator"
] 