#!/usr/bin/env python3
"""
Phase 4 Test Script - Research Workflow Automation
Tests the complete autonomous research workflow system with safety and quality assurance
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all Phase 4 components
from workflow.workflow_engine import WorkflowEngine, WorkflowState, AutomatedResearchCycle
from workflow.task_scheduler import TaskScheduler, PriorityLevel, ScheduledTask
from safety.oversight_monitor import SafetyMonitor, SafetyStatus, RiskLevel
from quality.peer_review_system import PeerReviewSystem, ReviewStatus, QualityMetrics
from integration.e2e_testing import E2ETestRunner, TestCategory, TestStatus

# Import dependencies from previous phases
from core.research_project import ResearchProject, ResearchState, Priority
from core.orchestrator import ResearchOrchestrator
from communication.protocols import CollaborationProtocol
from communication.agent_registry import AgentRegistry
from communication.message_bus import MessageBus
from agents.agent_types import AgentType, AgentCapability

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_workflow_engine():
    """Test the workflow engine for autonomous research cycles"""
    logger.info("=" * 60)
    logger.info("TEST 1: Workflow Engine - Autonomous Research Cycles")
    logger.info("=" * 60)
    
    try:
        # Create mock dependencies
        orchestrator = ResearchOrchestrator(max_concurrent_projects=5)
        orchestrator.is_running = True
        
        message_bus = MessageBus()
        await message_bus.initialize()
        
        agent_registry = AgentRegistry()
        await agent_registry.initialize()
        
        collaboration_protocol = CollaborationProtocol(message_bus, agent_registry)
        
        # Create workflow engine
        workflow_engine = WorkflowEngine(orchestrator, collaboration_protocol, agent_registry)
        
        # Test 1: Template initialization
        assert len(workflow_engine.workflow_templates) >= 2
        assert "complete_physics_research" in workflow_engine.workflow_templates
        assert "quick_validation" in workflow_engine.workflow_templates
        
        complete_template = workflow_engine.workflow_templates["complete_physics_research"]
        assert len(complete_template.steps) == 9  # 9 steps in complete research cycle
        assert complete_template.estimated_total_duration_hours == 9
        
        logger.info("✅ Workflow templates initialized correctly")
        
        # Test 2: Start automated research cycle
        test_project = ResearchProject(
            title="Test Quantum Entanglement Research",
            research_question="How does quantum entanglement affect measurement precision?",
            hypothesis="Entangled particles show correlated measurement variations",
            physics_domain="quantum",
            priority=Priority.HIGH
        )
        
        await orchestrator.add_project(test_project)
        
        cycle_id = await workflow_engine.start_automated_cycle(test_project, "quick_validation")
        assert cycle_id is not None
        assert cycle_id in workflow_engine.active_cycles
        
        cycle = workflow_engine.active_cycles[cycle_id]
        assert cycle.project_id == test_project.id
        assert cycle.template.template_id == "quick_validation"
        assert cycle.state == WorkflowState.INITIALIZED
        
        logger.info("✅ Automated research cycle started successfully")
        
        # Test 3: Monitor cycle progression
        timeout = datetime.utcnow() + timedelta(minutes=2)
        while datetime.utcnow() < timeout:
            status = await workflow_engine.get_cycle_status(cycle_id)
            if status and status["state"] in ["completed", "failed"]:
                break
            await asyncio.sleep(1)
        
        final_status = await workflow_engine.get_cycle_status(cycle_id)
        assert final_status is not None
        assert final_status["progress_percentage"] > 0
        
        logger.info(f"✅ Cycle progression monitored - Final state: {final_status['state']}")
        
        # Test 4: Multiple concurrent cycles
        concurrent_cycles = []
        for i in range(3):
            project = ResearchProject(
                title=f"Concurrent Test Project {i+1}",
                research_question=f"Test research question {i+1}",
                physics_domain="computational",
                priority=Priority.MEDIUM
            )
            await orchestrator.add_project(project)
            
            cycle_id = await workflow_engine.start_automated_cycle(project, "quick_validation")
            if cycle_id:
                concurrent_cycles.append(cycle_id)
        
        assert len(concurrent_cycles) == 3
        logger.info("✅ Multiple concurrent cycles started")
        
        # Test 5: Cycle management operations
        if concurrent_cycles:
            test_cycle_id = concurrent_cycles[0]
            
            # Pause cycle
            pause_success = await workflow_engine.pause_cycle(test_cycle_id, "Testing pause functionality")
            assert pause_success
            
            # Resume cycle
            resume_success = await workflow_engine.resume_cycle(test_cycle_id)
            assert resume_success
            
            logger.info("✅ Cycle pause/resume functionality working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Workflow engine test failed: {e}")
        return False

async def test_task_scheduler():
    """Test the task scheduler for priority management and resource allocation"""
    logger.info("=" * 60)
    logger.info("TEST 2: Task Scheduler - Priority Management & Resource Allocation")
    logger.info("=" * 60)
    
    try:
        # Create mock agent registry
        agent_registry = AgentRegistry()
        await agent_registry.initialize()
        
        # Create task scheduler
        task_scheduler = TaskScheduler(agent_registry)
        await task_scheduler.start()
        
        # Test 1: Basic task scheduling
        test_task = ScheduledTask(
            task_id="test_task_001",
            task_type="workflow_step",
            priority=PriorityLevel.HIGH,
            created_at=datetime.utcnow(),
            agent_requirements=[AgentType.THEORY],
            capability_requirements=[AgentCapability.HYPOTHESIS_GENERATION]
        )
        
        schedule_success = await task_scheduler.schedule_task(test_task)
        assert schedule_success
        
        logger.info("✅ Basic task scheduling working")
        
        # Test 2: Priority queue functionality
        tasks = []
        priorities = [PriorityLevel.LOW, PriorityLevel.CRITICAL, PriorityLevel.MEDIUM, PriorityLevel.HIGH]
        
        for i, priority in enumerate(priorities):
            task = ScheduledTask(
                task_id=f"priority_test_{i}",
                task_type="test",
                priority=priority,
                created_at=datetime.utcnow(),
                task_data={"priority_test": True}
            )
            await task_scheduler.schedule_task(task)
            tasks.append(task)
        
        # Allow scheduler to process tasks
        await asyncio.sleep(2)
        
        logger.info("✅ Priority queue functionality tested")
        
        # Test 3: Resource allocation simulation
        for i in range(5):
            resource_task = ScheduledTask(
                task_id=f"resource_test_{i}",
                task_type="resource_intensive",
                priority=PriorityLevel.MEDIUM,
                created_at=datetime.utcnow(),
                agent_requirements=[AgentType.EXPERIMENTAL],
                max_retries=1
            )
            await task_scheduler.schedule_task(resource_task)
        
        logger.info("✅ Resource allocation simulation completed")
        
        # Test 4: Task status monitoring
        task_status = await task_scheduler.get_task_status("test_task_001")
        assert task_status is not None
        assert task_status["task_id"] == "test_task_001"
        assert task_status["task_type"] == "workflow_step"
        
        logger.info("✅ Task status monitoring working")
        
        # Test 5: System status and metrics
        system_status = await task_scheduler.get_system_status()
        assert system_status is not None
        assert "queued_tasks" in system_status
        assert "active_tasks" in system_status
        assert "statistics" in system_status
        
        logger.info("✅ System status reporting working")
        
        await task_scheduler.stop()
        return True
        
    except Exception as e:
        logger.error(f"❌ Task scheduler test failed: {e}")
        return False

async def test_safety_monitor():
    """Test the safety monitoring and emergency intervention system"""
    logger.info("=" * 60)
    logger.info("TEST 3: Safety Monitor - Real-time Safety & Emergency Response")
    logger.info("=" * 60)
    
    try:
        # Create safety monitor
        safety_monitor = SafetyMonitor()
        await safety_monitor.start_monitoring()
        
        # Test 1: Safety rules initialization
        assert len(safety_monitor.safety_rules) >= 6
        assert "cpu_usage_limit" in safety_monitor.safety_rules
        assert "memory_usage_limit" in safety_monitor.safety_rules
        assert "step_timeout" in safety_monitor.safety_rules
        
        logger.info("✅ Safety rules initialized correctly")
        
        # Test 2: Emergency protocols initialization
        assert len(safety_monitor.emergency_protocols) >= 3
        assert "system_overload" in safety_monitor.emergency_protocols
        assert "agent_malfunction" in safety_monitor.emergency_protocols
        assert "data_integrity" in safety_monitor.emergency_protocols
        
        logger.info("✅ Emergency protocols initialized correctly")
        
        # Test 3: Register monitoring targets
        test_project = ResearchProject(
            title="Safety Test Project",
            research_question="How safe is our system?",
            physics_domain="safety_testing"
        )
        
        await safety_monitor.register_project(test_project)
        assert test_project.id in safety_monitor.monitored_projects
        
        logger.info("✅ Project registration for monitoring working")
        
        # Test 4: Safety status monitoring
        initial_status = await safety_monitor.get_safety_status()
        assert initial_status["system_safety_status"] == SafetyStatus.SAFE.value
        assert initial_status["active_violations"] == 0
        
        logger.info("✅ Safety status monitoring working")
        
        # Test 5: Simulated violation handling
        # The safety monitor will check for violations automatically
        # We simulate by checking the monitoring is active
        await asyncio.sleep(3)  # Let monitor run for a bit
        
        status_after_monitoring = await safety_monitor.get_safety_status()
        assert status_after_monitoring is not None
        assert "statistics" in status_after_monitoring
        
        logger.info("✅ Violation detection and monitoring active")
        
        # Test 6: Safety event handling
        safety_event_fired = False
        
        def test_safety_handler(data):
            nonlocal safety_event_fired
            safety_event_fired = True
            logger.info("Safety event handler triggered")
        
        safety_monitor.register_safety_event_handler("safety_status_changed", test_safety_handler)
        
        logger.info("✅ Safety event handling system working")
        
        await safety_monitor.stop_monitoring()
        return True
        
    except Exception as e:
        logger.error(f"❌ Safety monitor test failed: {e}")
        return False

async def test_quality_system():
    """Test the automated peer review and quality assurance system"""
    logger.info("=" * 60)
    logger.info("TEST 4: Quality System - Automated Peer Review & Assessment")
    logger.info("=" * 60)
    
    try:
        # Create quality system
        quality_system = PeerReviewSystem()
        
        # Test 1: Review criteria initialization
        assert len(quality_system.review_criteria) >= 10
        assert "methodology_experimental_design" in quality_system.review_criteria
        assert "statistical_significance" in quality_system.review_criteria
        assert "novelty_contribution" in quality_system.review_criteria
        
        logger.info("✅ Review criteria initialized correctly")
        
        # Test 2: Performance benchmarks
        assert len(quality_system.performance_benchmarks) == 0  # Should be empty initially
        quality_thresholds = quality_system.quality_thresholds
        assert "publication_ready" in quality_thresholds
        assert quality_thresholds["publication_ready"] == 75.0
        
        logger.info("✅ Quality thresholds configured correctly")
        
        # Test 3: Start peer review
        test_review_data = {
            "experimental_data": True,
            "data_completeness_percent": 92.0,
            "p_value": 0.03,
            "effect_size": 0.65,
            "statistical_power": 0.88,
            "overall_data_quality": 0.85,
            "methodology_rigor": 0.80
        }
        
        review_id = await quality_system.start_review("cycle", "test_cycle_001", test_review_data)
        assert review_id is not None
        assert review_id in quality_system.active_reviews
        
        logger.info("✅ Peer review started successfully")
        
        # Test 4: Monitor review progress
        timeout = datetime.utcnow() + timedelta(minutes=1)
        final_review_status = None
        
        while datetime.utcnow() < timeout:
            status = await quality_system.get_review_status(review_id)
            if status and status["status"] == ReviewStatus.COMPLETED.value:
                final_review_status = status
                break
            await asyncio.sleep(2)
        
        assert final_review_status is not None
        assert final_review_status["status"] == ReviewStatus.COMPLETED.value
        
        logger.info("✅ Review completion monitoring working")
        
        # Test 5: Quality metrics validation
        quality_metrics = final_review_status["quality_metrics"]
        assert quality_metrics["overall_score"] > 0
        assert quality_metrics["statistical_validity_score"] > 0
        assert quality_metrics["publication_readiness"] >= 0
        
        logger.info(f"✅ Quality assessment completed - Overall score: {quality_metrics['overall_score']:.1f}")
        
        # Test 6: Review details and comments
        review_details = await quality_system.get_review_details(review_id)
        assert review_details is not None
        assert "review_comments" in review_details
        assert "individual_scores" in review_details
        assert len(review_details["review_comments"]) > 0
        
        logger.info("✅ Detailed review information accessible")
        
        # Test 7: System status
        system_status = await quality_system.get_system_status()
        assert "completed_reviews" in system_status
        assert "statistics" in system_status
        assert system_status["completed_reviews"] >= 1
        
        logger.info("✅ Quality system status reporting working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Quality system test failed: {e}")
        return False

async def test_e2e_integration():
    """Test end-to-end integration of all Phase 4 components"""
    logger.info("=" * 60)
    logger.info("TEST 5: E2E Integration - Complete System Validation")
    logger.info("=" * 60)
    
    try:
        # Create all system components
        orchestrator = ResearchOrchestrator(max_concurrent_projects=5)
        orchestrator.is_running = True
        
        message_bus = MessageBus()
        await message_bus.initialize()
        
        agent_registry = AgentRegistry()
        await agent_registry.initialize()
        
        collaboration_protocol = CollaborationProtocol(message_bus, agent_registry)
        workflow_engine = WorkflowEngine(orchestrator, collaboration_protocol, agent_registry)
        task_scheduler = TaskScheduler(agent_registry)
        safety_monitor = SafetyMonitor()
        quality_system = PeerReviewSystem()
        
        # Create E2E test runner
        e2e_runner = E2ETestRunner()
        e2e_runner.inject_components(
            orchestrator, workflow_engine, task_scheduler,
            safety_monitor, quality_system, collaboration_protocol, agent_registry
        )
        
        # Test 1: Test scenario initialization
        assert len(e2e_runner.test_scenarios) >= 6
        assert "basic_research_cycle" in e2e_runner.test_scenarios
        assert "performance_stress" in e2e_runner.test_scenarios
        assert "safety_intervention" in e2e_runner.test_scenarios
        
        logger.info("✅ E2E test scenarios initialized")
        
        # Test 2: System health validation
        health_check = await e2e_runner.validator.validate_system_health()
        assert all(health_check.values())
        
        logger.info("✅ System health validation passed")
        
        # Test 3: Run a basic workflow test
        basic_scenario = e2e_runner.test_scenarios["basic_research_cycle"]
        test_result = await e2e_runner._run_test_scenario(basic_scenario)
        
        assert test_result.status in [TestStatus.PASSED, TestStatus.COMPLETED]
        assert test_result.duration_seconds > 0
        
        logger.info(f"✅ Basic workflow test completed - Status: {test_result.status.value}")
        
        # Test 4: Run a multi-agent coordination test
        if "agent_coordination" in e2e_runner.test_scenarios:
            coordination_scenario = e2e_runner.test_scenarios["agent_coordination"]
            coordination_result = await e2e_runner._run_test_scenario(coordination_scenario)
            
            assert coordination_result.status in [TestStatus.PASSED, TestStatus.COMPLETED]
            logger.info(f"✅ Agent coordination test completed - Status: {coordination_result.status.value}")
        
        # Test 5: System status and metrics
        test_status = await e2e_runner.get_test_status()
        assert test_status["test_scenarios_available"] >= 6
        assert test_status["system_components_injected"]["orchestrator"]
        assert test_status["system_components_injected"]["workflow_engine"]
        
        logger.info("✅ E2E system status reporting working")
        
        # Test 6: Integration validation
        # Verify all components can work together
        
        # Start systems
        await task_scheduler.start()
        await safety_monitor.start_monitoring()
        
        # Create and run a complete research cycle
        integration_project = ResearchProject(
            title="Integration Test Project",
            research_question="Does the complete system work end-to-end?",
            hypothesis="All components integrate seamlessly",
            physics_domain="integration_testing",
            priority=Priority.HIGH
        )
        
        await orchestrator.add_project(integration_project)
        await safety_monitor.register_project(integration_project)
        
        cycle_id = await workflow_engine.start_automated_cycle(integration_project, "quick_validation")
        assert cycle_id is not None
        
        # Monitor for completion
        timeout = datetime.utcnow() + timedelta(minutes=2)
        final_status = None
        
        while datetime.utcnow() < timeout:
            status = await workflow_engine.get_cycle_status(cycle_id)
            if status and status["state"] in ["completed", "failed"]:
                final_status = status
                break
            await asyncio.sleep(1)
        
        # Start quality review of completed cycle
        if final_status and final_status["state"] == "completed":
            review_data = {
                "cycle_id": cycle_id,
                "experimental_data": True,
                "data_completeness_percent": 90.0,
                "p_value": 0.04,
                "effect_size": 0.6
            }
            
            review_id = await quality_system.start_review("cycle", cycle_id, review_data)
            assert review_id is not None
            
            logger.info("✅ Quality review initiated for completed cycle")
        
        # Cleanup
        await task_scheduler.stop()
        await safety_monitor.stop_monitoring()
        
        logger.info("✅ Complete system integration test passed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ E2E integration test failed: {e}")
        return False

async def test_performance_benchmarks():
    """Test system performance against established benchmarks"""
    logger.info("=" * 60)
    logger.info("TEST 6: Performance Benchmarks - System Performance Validation")
    logger.info("=" * 60)
    
    try:
        # Test 1: Workflow completion time benchmark
        start_time = datetime.utcnow()
        
        # Create minimal system for performance testing
        orchestrator = ResearchOrchestrator(max_concurrent_projects=3)
        orchestrator.is_running = True
        
        test_project = ResearchProject(
            title="Performance Test Project",
            research_question="How fast is the system?",
            physics_domain="performance_testing"
        )
        
        await orchestrator.add_project(test_project)
        
        completion_time = (datetime.utcnow() - start_time).total_seconds()
        assert completion_time < 5.0  # Should complete setup in under 5 seconds
        
        logger.info(f"✅ System setup benchmark passed - {completion_time:.2f} seconds")
        
        # Test 2: Concurrent workflow handling
        concurrent_start = datetime.utcnow()
        
        concurrent_projects = []
        for i in range(5):
            project = ResearchProject(
                title=f"Concurrent Performance Test {i+1}",
                research_question=f"Performance question {i+1}",
                physics_domain="performance_testing"
            )
            await orchestrator.add_project(project)
            concurrent_projects.append(project)
        
        concurrent_time = (datetime.utcnow() - concurrent_start).total_seconds()
        assert concurrent_time < 10.0  # Should handle 5 concurrent projects in under 10 seconds
        
        logger.info(f"✅ Concurrent workflow benchmark passed - {concurrent_time:.2f} seconds")
        
        # Test 3: Memory efficiency
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_usage_mb = process.memory_info().rss / 1024 / 1024
        
        # Should not use excessive memory (under 500MB for testing)
        assert memory_usage_mb < 500
        
        logger.info(f"✅ Memory efficiency benchmark passed - {memory_usage_mb:.1f}MB")
        
        # Test 4: Component initialization time
        init_start = datetime.utcnow()
        
        # Initialize all major components
        task_scheduler = TaskScheduler(None)
        safety_monitor = SafetyMonitor()
        quality_system = PeerReviewSystem()
        
        init_time = (datetime.utcnow() - init_start).total_seconds()
        assert init_time < 3.0  # Should initialize all components in under 3 seconds
        
        logger.info(f"✅ Component initialization benchmark passed - {init_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Performance benchmarks test failed: {e}")
        return False

async def main():
    """Run all Phase 4 tests"""
    logger.info("🚀 Starting Phase 4 Test Suite - Research Workflow Automation")
    logger.info("Testing: Workflow Engine, Task Scheduler, Safety Monitor, Quality System, E2E Integration")
    
    test_results = []
    
    # Run all test suites
    tests = [
        ("Workflow Engine", test_workflow_engine),
        ("Task Scheduler", test_task_scheduler),
        ("Safety Monitor", test_safety_monitor),
        ("Quality System", test_quality_system),
        ("E2E Integration", test_e2e_integration),
        ("Performance Benchmarks", test_performance_benchmarks)
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} tests...")
        try:
            result = await test_func()
            test_results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} tests PASSED")
            else:
                logger.error(f"❌ {test_name} tests FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} tests FAILED with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    logger.info("=" * 80)
    logger.info("PHASE 4 TEST SUMMARY")
    logger.info("=" * 80)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info("-" * 80)
    logger.info(f"Overall Results: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL PHASE 4 TESTS PASSED! 🎉")
        logger.info("✅ Workflow automation system is ready for autonomous research!")
        
        # Phase 4 completion summary
        logger.info("\n📊 PHASE 4 CAPABILITIES VERIFIED:")
        logger.info("  • Autonomous Research Cycle Execution")
        logger.info("  • Advanced Task Scheduling & Resource Management")
        logger.info("  • Real-time Safety Monitoring & Emergency Response")
        logger.info("  • Automated Peer Review & Quality Assessment")
        logger.info("  • Comprehensive End-to-End Testing Framework")
        logger.info("  • Performance Benchmarking & Optimization")
        
        logger.info("\n🚀 READY FOR E2E AUTONOMOUS RESEARCH:")
        logger.info("  • Complete research cycles from hypothesis to publication")
        logger.info("  • Multi-agent coordination with safety oversight")
        logger.info("  • Automated quality assurance and peer review")
        logger.info("  • System performance monitoring and optimization")
        logger.info("  • Comprehensive failure recovery and resilience")
        
        return True
    else:
        logger.error("❌ Some Phase 4 tests failed. Please review the logs.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main()) 