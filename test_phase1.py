#!/usr/bin/env python3
"""
Phase 1 Test Script - Core Orchestrator Engine
Tests the foundational research project management and orchestration functionality
"""

import asyncio
import logging
import json
from datetime import datetime
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.research_project import ResearchProject, ResearchState, Priority
from core.orchestrator import ResearchOrchestrator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """Test basic Phase 1 functionality"""
    logger.info("=" * 60)
    logger.info("PHASE 1 TESTING - Core Orchestrator Engine")
    logger.info("=" * 60)
    
    # Test 1: Project Creation
    logger.info("Test 1: Creating research project...")
    project = ResearchProject(
        title="Test Quantum Research",
        research_question="How does quantum entanglement work?",
        physics_domain="quantum",
        priority=Priority.HIGH
    )
    
    assert project.id is not None
    assert project.state == ResearchState.INITIAL
    logger.info(f"✅ Project created: {project.title} (ID: {project.id})")
    
    # Test 2: State Management
    logger.info("Test 2: Testing state management...")
    project.update_state(ResearchState.PLANNING, "Starting research")
    project.update_progress(25.0, "Initial progress")
    project.assign_agent("test_agent", "primary")
    
    assert project.state == ResearchState.PLANNING
    assert project.metrics.progress_percentage == 25.0
    assert project.primary_agent == "test_agent"
    logger.info("✅ State management working")
    
    # Test 3: Orchestrator
    logger.info("Test 3: Testing orchestrator...")
    orchestrator = ResearchOrchestrator(max_concurrent_projects=3)
    orchestrator.is_running = True
    orchestrator.available_agents = {"theory_agent", "experimental_agent"}
    
    new_project = await orchestrator.create_project(
        title="Orchestrator Test",
        research_question="Does orchestration work?",
        physics_domain="optics"
    )
    
    assert len(orchestrator.active_projects) == 1
    assert orchestrator.stats["projects_created"] == 1
    logger.info("✅ Orchestrator working")
    
    # Test 4: System Status
    logger.info("Test 4: Testing system status...")
    status = orchestrator.get_system_status()
    
    assert status["is_running"] == True
    assert "projects" in status
    assert "agents" in status
    logger.info("✅ System status working")
    
    logger.info("=" * 60)
    logger.info("🎉 ALL PHASE 1 TESTS PASSED!")
    logger.info("✅ Core orchestrator engine is functional")
    logger.info("✅ Ready to proceed to Phase 2")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_basic_functionality()) 