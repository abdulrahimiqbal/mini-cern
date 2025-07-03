"""
Science Research Institute - Core Module
Central orchestration engine for autonomous research projects
"""

from .research_project import ResearchProject, ResearchState
from .orchestrator import ResearchOrchestrator

__all__ = ['ResearchProject', 'ResearchState', 'ResearchOrchestrator'] 