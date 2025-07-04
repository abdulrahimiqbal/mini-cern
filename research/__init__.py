"""
Phase 6: Advanced AI Research Module
Autonomous research capabilities for scientific discovery
"""

from .orchestration import ResearchOrchestrator
from .advanced_llm import AdvancedLLMManager, TaskType, ResearchContext

__version__ = "6.0.0"
__all__ = [
    "ResearchOrchestrator",
    "AdvancedLLMManager", 
    "TaskType",
    "ResearchContext"
] 