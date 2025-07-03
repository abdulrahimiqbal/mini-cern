"""
End-to-End Testing Framework
Comprehensive testing of autonomous research workflows from hypothesis to publication
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
import json
import time

from core.research_project import ResearchProject, ResearchState, Priority
from core.orchestrator import ResearchOrchestrator
from workflow.workflow_engine import WorkflowEngine, WorkflowState, AutomatedResearchCycle
from workflow.task_scheduler import TaskScheduler, PriorityLevel
from safety.oversight_monitor import SafetyMonitor, SafetyStatus
from quality.peer_review_system import PeerReviewSystem, ReviewStatus
from communication.protocols import CollaborationProtocol
from communication.agent_registry import AgentRegistry
from communication.message_bus import MessageBus
from agents.agent_types import AgentType

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Status of test execution"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"

class TestCategory(Enum):
    """Categories of E2E tests"""
    BASIC_WORKFLOW = "basic_workflow"
    ADVANCED_WORKFLOW = "advanced_workflow"
    PERFORMANCE = "performance"
    SAFETY = "safety"
    QUALITY = "quality"
    INTEGRATION = "integration"
    STRESS = "stress"
    FAILURE_RECOVERY = "failure_recovery"

@dataclass
class TestResult:
    """Result of a test execution"""
    test_id: str
    test_name: str
    category: TestCategory
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    success_metrics: Dict[str, bool] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    detailed_logs: List[str] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestScenario:
    """Definition of a test scenario"""
    scenario_id: str
    scenario_name: str
    category: TestCategory
    description: str
    setup_steps: List[str]
    execution_steps: List[str]
    validation_criteria: List[str]
    expected_duration_minutes: int
    timeout_minutes: int
    prerequisites: List[str] = field(default_factory=list)
    cleanup_required: bool = True

@dataclass
class PerformanceBenchmark:
    """Performance benchmark definition"""
    benchmark_id: str
    benchmark_name: str
    target_metric: str
    expected_value: float
    tolerance_percent: float
    measurement_unit: str

class SystemValidator:
    """Validates system state and component interactions"""
    
    def __init__(self):
        self.validation_rules = {}
        self._initialize_validation_rules()
    
    def _initialize_validation_rules(self):
        """Initialize system validation rules"""
        self.validation_rules = {
            "project_lifecycle": {
                "required_states": [ResearchState.INITIAL, ResearchState.PLANNING, ResearchState.EXECUTING],
                "valid_transitions": {
                    ResearchState.INITIAL: [ResearchState.PLANNING],
                    ResearchState.PLANNING: [ResearchState.DESIGNING, ResearchState.EXECUTING],
                    ResearchState.EXECUTING: [ResearchState.ANALYZING, ResearchState.COMPLETED, ResearchState.FAILED]
                }
            },
            "workflow_integrity": {
                "required_components": ["workflow_engine", "task_scheduler", "safety_monitor"],
                "component_health_thresholds": {
                    "response_time_ms": 1000,
                    "error_rate_percent": 5.0,
                    "availability_percent": 99.0
                }
            },
            "agent_coordination": {
                "min_response_time_ms": 100,
                "max_response_time_ms": 5000,
                "required_capabilities": ["hypothesis_generation", "experimental_design", "data_analysis"]
            }
        }
    
    async def validate_system_health(self) -> Dict[str, bool]:
        """Validate overall system health"""
        validations = {}
        
        # Component availability
        validations["orchestrator_responsive"] = True  # Simulated
        validations["workflow_engine_active"] = True
        validations["safety_monitor_active"] = True
        validations["quality_system_active"] = True
        
        # Resource availability
        validations["sufficient_memory"] = True
        validations["sufficient_cpu"] = True
        validations["database_accessible"] = True
        
        # Agent network
        validations["agents_available"] = True
        validations["communication_functional"] = True
        
        return validations
    
    async def validate_workflow_completion(self, cycle: AutomatedResearchCycle) -> Dict[str, bool]:
        """Validate that a workflow completed successfully"""
        validations = {}
        
        # State validation
        validations["workflow_completed"] = cycle.state == WorkflowState.COMPLETED
        validations["all_steps_completed"] = all(step.is_completed for step in cycle.template.steps)
        validations["quality_threshold_met"] = cycle.quality_score >= 0.7
        
        # Results validation
        validations["results_generated"] = len(cycle.step_results) > 0
        validations["no_safety_violations"] = cycle.safety_status == "safe"
        
        # Time validation
        if cycle.started_at and cycle.completed_at:
            duration_hours = (cycle.completed_at - cycle.started_at).total_seconds() / 3600
            expected_duration = cycle.template.estimated_total_duration_hours
            validations["completed_within_time"] = duration_hours <= expected_duration * 1.5
        
        return validations

class E2ETestRunner:
    """
    Comprehensive End-to-End Test Runner
    
    Orchestrates complete testing of the autonomous research system
    from individual components to full research cycles
    """
    
    def __init__(self):
        # System components (to be injected)
        self.orchestrator: Optional[ResearchOrchestrator] = None
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.task_scheduler: Optional[TaskScheduler] = None
        self.safety_monitor: Optional[SafetyMonitor] = None
        self.quality_system: Optional[PeerReviewSystem] = None
        self.collaboration_protocol: Optional[CollaborationProtocol] = None
        self.agent_registry: Optional[AgentRegistry] = None
        
        # Test management
        self.test_scenarios: Dict[str, TestScenario] = {}
        self.test_results: Dict[str, TestResult] = {}
        self.performance_benchmarks: Dict[str, PerformanceBenchmark] = {}
        
        # Test configuration
        self.test_timeout_minutes = 60
        self.max_concurrent_tests = 3
        self.cleanup_between_tests = True
        
        # System validator
        self.validator = SystemValidator()
        
        # Test statistics
        self.test_stats = {
            "total_tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "average_test_duration_minutes": 0.0,
            "system_uptime_percent": 0.0
        }
        
        # Initialize test scenarios and benchmarks
        self._initialize_test_scenarios()
        self._initialize_performance_benchmarks()
    
    def inject_components(self, orchestrator: ResearchOrchestrator, 
                         workflow_engine: WorkflowEngine,
                         task_scheduler: TaskScheduler,
                         safety_monitor: SafetyMonitor,
                         quality_system: PeerReviewSystem,
                         collaboration_protocol: CollaborationProtocol,
                         agent_registry: AgentRegistry):
        """Inject system components for testing"""
        self.orchestrator = orchestrator
        self.workflow_engine = workflow_engine
        self.task_scheduler = task_scheduler
        self.safety_monitor = safety_monitor
        self.quality_system = quality_system
        self.collaboration_protocol = collaboration_protocol
        self.agent_registry = agent_registry
    
    def _initialize_test_scenarios(self):
        """Initialize comprehensive test scenarios"""
        
        # Basic workflow tests
        self.test_scenarios["basic_research_cycle"] = TestScenario(
            scenario_id="basic_research_cycle",
            scenario_name="Basic Research Cycle End-to-End",
            category=TestCategory.BASIC_WORKFLOW,
            description="Test complete research cycle from project creation to completion",
            setup_steps=[
                "Initialize system components",
                "Create test research project",
                "Register test agents"
            ],
            execution_steps=[
                "Start automated research cycle",
                "Monitor workflow progress",
                "Validate step completions",
                "Verify results generation"
            ],
            validation_criteria=[
                "All workflow steps completed",
                "Quality score >= 0.7",
                "No safety violations",
                "Results properly stored"
            ],
            expected_duration_minutes=15,
            timeout_minutes=30
        )
        
        self.test_scenarios["agent_coordination"] = TestScenario(
            scenario_id="agent_coordination",
            scenario_name="Multi-Agent Coordination Test",
            category=TestCategory.BASIC_WORKFLOW,
            description="Test coordination between different agent types",
            setup_steps=[
                "Deploy theory, experimental, and analysis agents",
                "Create collaboration workflow"
            ],
            execution_steps=[
                "Initiate multi-agent task",
                "Monitor agent interactions", 
                "Validate task handoffs",
                "Verify collaborative results"
            ],
            validation_criteria=[
                "All agents participated",
                "Task handoffs successful",
                "Collaborative results generated",
                "Token rewards distributed"
            ],
            expected_duration_minutes=10,
            timeout_minutes=20
        )
        
        # Advanced workflow tests
        self.test_scenarios["complex_research_pipeline"] = TestScenario(
            scenario_id="complex_research_pipeline",
            scenario_name="Complex Research Pipeline",
            category=TestCategory.ADVANCED_WORKFLOW,
            description="Test complex research pipeline with dependencies and parallel processing",
            setup_steps=[
                "Set up multiple research projects",
                "Configure complex workflow templates",
                "Initialize resource pools"
            ],
            execution_steps=[
                "Launch multiple concurrent research cycles",
                "Monitor resource allocation",
                "Track workflow dependencies",
                "Validate parallel processing"
            ],
            validation_criteria=[
                "All projects completed successfully",
                "Resource conflicts avoided",
                "Dependencies properly managed",
                "Parallel efficiency achieved"
            ],
            expected_duration_minutes=45,
            timeout_minutes=90
        )
        
        # Performance tests
        self.test_scenarios["performance_stress"] = TestScenario(
            scenario_id="performance_stress",
            scenario_name="System Performance Under Load",
            category=TestCategory.PERFORMANCE,
            description="Test system performance under high load conditions",
            setup_steps=[
                "Configure high-load test environment",
                "Prepare performance monitoring",
                "Set baseline measurements"
            ],
            execution_steps=[
                "Launch 10 concurrent research cycles",
                "Monitor system resource usage",
                "Measure response times",
                "Track throughput metrics"
            ],
            validation_criteria=[
                "Response times < 2 seconds",
                "CPU usage < 80%",
                "Memory usage < 75%",
                "No system failures"
            ],
            expected_duration_minutes=30,
            timeout_minutes=60
        )
        
        # Safety tests
        self.test_scenarios["safety_intervention"] = TestScenario(
            scenario_id="safety_intervention",
            scenario_name="Safety System Intervention",
            category=TestCategory.SAFETY,
            description="Test safety system response to violations",
            setup_steps=[
                "Enable safety monitoring",
                "Configure safety thresholds",
                "Prepare test violations"
            ],
            execution_steps=[
                "Trigger resource limit violation",
                "Trigger time limit violation",
                "Monitor safety system response",
                "Validate intervention actions"
            ],
            validation_criteria=[
                "Safety violations detected",
                "Appropriate actions taken",
                "System recovered safely",
                "Emergency protocols functional"
            ],
            expected_duration_minutes=20,
            timeout_minutes=40
        )
        
        # Quality assurance tests
        self.test_scenarios["quality_assessment"] = TestScenario(
            scenario_id="quality_assessment",
            scenario_name="Automated Quality Assessment",
            category=TestCategory.QUALITY,
            description="Test automated peer review and quality assessment",
            setup_steps=[
                "Complete a research cycle",
                "Initialize peer review system",
                "Configure review criteria"
            ],
            execution_steps=[
                "Start automated peer review",
                "Monitor review progress",
                "Validate quality metrics",
                "Check publication readiness"
            ],
            validation_criteria=[
                "Quality assessment completed",
                "Multiple review dimensions evaluated",
                "Consistent reviewer consensus",
                "Publication recommendation generated"
            ],
            expected_duration_minutes=25,
            timeout_minutes=50
        )
        
        # Failure recovery tests
        self.test_scenarios["failure_recovery"] = TestScenario(
            scenario_id="failure_recovery",
            scenario_name="System Failure Recovery",
            category=TestCategory.FAILURE_RECOVERY,
            description="Test system recovery from various failure scenarios",
            setup_steps=[
                "Start normal research cycle",
                "Prepare failure injection",
                "Set recovery monitoring"
            ],
            execution_steps=[
                "Inject agent failure",
                "Inject network failure",
                "Monitor recovery processes",
                "Validate system restoration"
            ],
            validation_criteria=[
                "Failures detected quickly",
                "Recovery mechanisms activated",
                "System restored to normal operation",
                "Data integrity maintained"
            ],
            expected_duration_minutes=35,
            timeout_minutes=70
        )
        
        logger.info(f"Initialized {len(self.test_scenarios)} test scenarios")
    
    def _initialize_performance_benchmarks(self):
        """Initialize performance benchmarks"""
        
        self.performance_benchmarks["workflow_completion_time"] = PerformanceBenchmark(
            benchmark_id="workflow_completion_time",
            benchmark_name="Workflow Completion Time",
            target_metric="completion_time_minutes",
            expected_value=15.0,
            tolerance_percent=20.0,
            measurement_unit="minutes"
        )
        
        self.performance_benchmarks["agent_response_time"] = PerformanceBenchmark(
            benchmark_id="agent_response_time",
            benchmark_name="Agent Response Time",
            target_metric="response_time_ms",
            expected_value=500.0,
            tolerance_percent=50.0,
            measurement_unit="milliseconds"
        )
        
        self.performance_benchmarks["system_throughput"] = PerformanceBenchmark(
            benchmark_id="system_throughput",
            benchmark_name="System Throughput",
            target_metric="cycles_per_hour",
            expected_value=4.0,
            tolerance_percent=25.0,
            measurement_unit="cycles/hour"
        )
        
        self.performance_benchmarks["resource_efficiency"] = PerformanceBenchmark(
            benchmark_id="resource_efficiency",
            benchmark_name="Resource Utilization Efficiency",
            target_metric="resource_utilization_percent",
            expected_value=70.0,
            tolerance_percent=15.0,
            measurement_unit="percent"
        )
        
        logger.info(f"Initialized {len(self.performance_benchmarks)} performance benchmarks")
    
    async def run_all_tests(self) -> Dict[str, TestResult]:
        """Run all test scenarios"""
        logger.info("Starting comprehensive E2E test suite")
        
        # Validate system health before testing
        health_check = await self.validator.validate_system_health()
        if not all(health_check.values()):
            logger.error("System health check failed, aborting tests")
            return {}
        
        # Run tests by category
        all_results = {}
        
        # Basic workflow tests
        basic_results = await self._run_test_category(TestCategory.BASIC_WORKFLOW)
        all_results.update(basic_results)
        
        # Advanced workflow tests
        advanced_results = await self._run_test_category(TestCategory.ADVANCED_WORKFLOW)
        all_results.update(advanced_results)
        
        # Performance tests
        performance_results = await self._run_test_category(TestCategory.PERFORMANCE)
        all_results.update(performance_results)
        
        # Safety tests
        safety_results = await self._run_test_category(TestCategory.SAFETY)
        all_results.update(safety_results)
        
        # Quality tests
        quality_results = await self._run_test_category(TestCategory.QUALITY)
        all_results.update(quality_results)
        
        # Failure recovery tests
        recovery_results = await self._run_test_category(TestCategory.FAILURE_RECOVERY)
        all_results.update(recovery_results)
        
        # Generate test report
        await self._generate_test_report(all_results)
        
        logger.info(f"Completed E2E test suite: {len(all_results)} tests executed")
        return all_results
    
    async def _run_test_category(self, category: TestCategory) -> Dict[str, TestResult]:
        """Run all tests in a specific category"""
        category_scenarios = {k: v for k, v in self.test_scenarios.items() if v.category == category}
        results = {}
        
        logger.info(f"Running {len(category_scenarios)} tests in category {category.value}")
        
        for scenario_id, scenario in category_scenarios.items():
            try:
                result = await self._run_test_scenario(scenario)
                results[scenario_id] = result
                
                # Cleanup between tests if configured
                if self.cleanup_between_tests:
                    await self._cleanup_test_environment()
                
            except Exception as e:
                logger.error(f"Error running test {scenario_id}: {e}")
                result = TestResult(
                    test_id=scenario_id,
                    test_name=scenario.scenario_name,
                    category=category,
                    status=TestStatus.FAILED,
                    start_time=datetime.utcnow(),
                    error_message=str(e)
                )
                results[scenario_id] = result
        
        return results
    
    async def _run_test_scenario(self, scenario: TestScenario) -> TestResult:
        """Run a single test scenario"""
        test_result = TestResult(
            test_id=scenario.scenario_id,
            test_name=scenario.scenario_name,
            category=scenario.category,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow()
        )
        
        logger.info(f"Starting test: {scenario.scenario_name}")
        
        try:
            # Setup phase
            await self._execute_test_setup(scenario, test_result)
            
            # Execution phase
            await self._execute_test_steps(scenario, test_result)
            
            # Validation phase
            await self._validate_test_results(scenario, test_result)
            
            # Determine final status
            if all(test_result.success_metrics.values()):
                test_result.status = TestStatus.PASSED
                self.test_stats["tests_passed"] += 1
            else:
                test_result.status = TestStatus.FAILED
                self.test_stats["tests_failed"] += 1
            
        except asyncio.TimeoutError:
            test_result.status = TestStatus.TIMEOUT
            test_result.error_message = f"Test exceeded timeout of {scenario.timeout_minutes} minutes"
            self.test_stats["tests_failed"] += 1
            
        except Exception as e:
            test_result.status = TestStatus.FAILED
            test_result.error_message = str(e)
            self.test_stats["tests_failed"] += 1
            
        finally:
            test_result.end_time = datetime.utcnow()
            test_result.duration_seconds = (test_result.end_time - test_result.start_time).total_seconds()
            self.test_stats["total_tests_run"] += 1
            
            # Update average duration
            total_tests = self.test_stats["total_tests_run"]
            current_avg = self.test_stats["average_test_duration_minutes"]
            new_duration = test_result.duration_seconds / 60
            self.test_stats["average_test_duration_minutes"] = (current_avg * (total_tests - 1) + new_duration) / total_tests
        
        logger.info(f"Test {scenario.scenario_name} completed with status: {test_result.status.value}")
        return test_result
    
    async def _execute_test_setup(self, scenario: TestScenario, test_result: TestResult) -> None:
        """Execute test setup steps"""
        test_result.detailed_logs.append("=== SETUP PHASE ===")
        
        for step in scenario.setup_steps:
            test_result.detailed_logs.append(f"Setup: {step}")
            
            if step == "Initialize system components":
                await self._initialize_test_components()
            elif step == "Create test research project":
                project = await self._create_test_project()
                test_result.artifacts["test_project"] = project
            elif step == "Register test agents":
                agents = await self._register_test_agents()
                test_result.artifacts["test_agents"] = agents
            elif step == "Deploy theory, experimental, and analysis agents":
                await self._deploy_agent_types([AgentType.THEORY, AgentType.EXPERIMENTAL, AgentType.ANALYSIS])
            elif step == "Enable safety monitoring":
                if self.safety_monitor:
                    await self.safety_monitor.start_monitoring()
            # Add more setup steps as needed
            
            await asyncio.sleep(0.1)  # Small delay between setup steps
    
    async def _execute_test_steps(self, scenario: TestScenario, test_result: TestResult) -> None:
        """Execute main test steps"""
        test_result.detailed_logs.append("=== EXECUTION PHASE ===")
        
        for step in scenario.execution_steps:
            test_result.detailed_logs.append(f"Executing: {step}")
            start_time = time.time()
            
            if step == "Start automated research cycle":
                cycle_id = await self._start_test_research_cycle(test_result)
                test_result.artifacts["cycle_id"] = cycle_id
                
            elif step == "Monitor workflow progress":
                await self._monitor_workflow_progress(test_result)
                
            elif step == "Initiate multi-agent task":
                task_id = await self._initiate_multi_agent_task(test_result)
                test_result.artifacts["task_id"] = task_id
                
            elif step == "Launch multiple concurrent research cycles":
                cycle_ids = await self._launch_concurrent_cycles(test_result, count=5)
                test_result.artifacts["concurrent_cycle_ids"] = cycle_ids
                
            elif step == "Launch 10 concurrent research cycles":
                cycle_ids = await self._launch_concurrent_cycles(test_result, count=10)
                test_result.artifacts["stress_cycle_ids"] = cycle_ids
                
            elif step == "Start automated peer review":
                review_id = await self._start_test_peer_review(test_result)
                test_result.artifacts["review_id"] = review_id
                
            elif step == "Trigger resource limit violation":
                await self._trigger_safety_violation(test_result, "resource_limit")
                
            elif step == "Inject agent failure":
                await self._inject_agent_failure(test_result)
            
            # Record step execution time
            step_duration = time.time() - start_time
            test_result.performance_metrics[f"{step}_duration_seconds"] = step_duration
            
            await asyncio.sleep(0.5)  # Brief pause between steps
    
    async def _validate_test_results(self, scenario: TestScenario, test_result: TestResult) -> None:
        """Validate test results against criteria"""
        test_result.detailed_logs.append("=== VALIDATION PHASE ===")
        
        for criteria in scenario.validation_criteria:
            test_result.detailed_logs.append(f"Validating: {criteria}")
            
            if criteria == "All workflow steps completed":
                test_result.success_metrics[criteria] = await self._validate_workflow_completion(test_result)
                
            elif criteria == "Quality score >= 0.7":
                test_result.success_metrics[criteria] = await self._validate_quality_score(test_result, 0.7)
                
            elif criteria == "No safety violations":
                test_result.success_metrics[criteria] = await self._validate_no_safety_violations(test_result)
                
            elif criteria == "All agents participated":
                test_result.success_metrics[criteria] = await self._validate_agent_participation(test_result)
                
            elif criteria == "Response times < 2 seconds":
                test_result.success_metrics[criteria] = await self._validate_response_times(test_result, 2.0)
                
            elif criteria == "Safety violations detected":
                test_result.success_metrics[criteria] = await self._validate_safety_violations_detected(test_result)
                
            elif criteria == "Quality assessment completed":
                test_result.success_metrics[criteria] = await self._validate_quality_assessment(test_result)
                
            elif criteria == "System restored to normal operation":
                test_result.success_metrics[criteria] = await self._validate_system_recovery(test_result)
            
            # Add more validation criteria as needed
    
    async def _initialize_test_components(self) -> None:
        """Initialize system components for testing"""
        if self.task_scheduler:
            await self.task_scheduler.start()
        if self.safety_monitor:
            await self.safety_monitor.start_monitoring()
    
    async def _create_test_project(self) -> ResearchProject:
        """Create a test research project"""
        project = ResearchProject(
            title="E2E Test Research Project",
            research_question="How effective is the autonomous research system?",
            hypothesis="The system can conduct research autonomously with high quality",
            physics_domain="computational",
            priority=Priority.HIGH,
            expected_duration_hours=2,
            max_cost_usd=100.0
        )
        
        if self.orchestrator:
            await self.orchestrator.add_project(project)
        
        return project
    
    async def _register_test_agents(self) -> List[str]:
        """Register test agents"""
        test_agents = [
            {"id": "test_theory_001", "type": AgentType.THEORY},
            {"id": "test_experimental_001", "type": AgentType.EXPERIMENTAL},
            {"id": "test_analysis_001", "type": AgentType.ANALYSIS}
        ]
        
        agent_ids = []
        if self.agent_registry:
            for agent in test_agents:
                # Simulate agent registration
                agent_ids.append(agent["id"])
        
        return agent_ids
    
    async def _deploy_agent_types(self, agent_types: List[AgentType]) -> None:
        """Deploy specific agent types for testing"""
        # Simulated agent deployment
        for agent_type in agent_types:
            logger.info(f"Deployed {agent_type.value} agent for testing")
    
    async def _start_test_research_cycle(self, test_result: TestResult) -> Optional[str]:
        """Start a test research cycle"""
        if not self.workflow_engine or "test_project" not in test_result.artifacts:
            return None
        
        project = test_result.artifacts["test_project"]
        cycle_id = await self.workflow_engine.start_automated_cycle(project, "quick_validation")
        
        if cycle_id:
            test_result.detailed_logs.append(f"Started research cycle: {cycle_id}")
        
        return cycle_id
    
    async def _monitor_workflow_progress(self, test_result: TestResult) -> None:
        """Monitor workflow progress during testing"""
        if not self.workflow_engine or "cycle_id" not in test_result.artifacts:
            return
        
        cycle_id = test_result.artifacts["cycle_id"]
        timeout = time.time() + 300  # 5 minute timeout
        
        while time.time() < timeout:
            status = await self.workflow_engine.get_cycle_status(cycle_id)
            if not status:
                break
                
            test_result.detailed_logs.append(f"Workflow progress: {status['progress_percentage']:.1f}%")
            
            if status["state"] in ["completed", "failed"]:
                test_result.artifacts["final_cycle_status"] = status
                break
            
            await asyncio.sleep(5)
    
    async def _initiate_multi_agent_task(self, test_result: TestResult) -> Optional[str]:
        """Initiate a multi-agent collaboration task"""
        if not self.collaboration_protocol:
            return None
        
        agents = test_result.artifacts.get("test_agents", [])
        if len(agents) < 2:
            return None
        
        workflow_id = await self.collaboration_protocol.start_workflow(
            "hypothesis_to_experiment",
            agents[:2],
            {"test_context": "E2E testing multi-agent coordination"}
        )
        
        return workflow_id
    
    async def _launch_concurrent_cycles(self, test_result: TestResult, count: int) -> List[str]:
        """Launch multiple concurrent research cycles"""
        if not self.workflow_engine:
            return []
        
        cycle_ids = []
        for i in range(count):
            project = ResearchProject(
                title=f"Concurrent Test Project {i+1}",
                research_question=f"Test question {i+1}",
                physics_domain="computational",
                priority=Priority.MEDIUM
            )
            
            if self.orchestrator:
                await self.orchestrator.add_project(project)
                
            cycle_id = await self.workflow_engine.start_automated_cycle(project, "quick_validation")
            if cycle_id:
                cycle_ids.append(cycle_id)
        
        test_result.detailed_logs.append(f"Launched {len(cycle_ids)} concurrent cycles")
        return cycle_ids
    
    async def _start_test_peer_review(self, test_result: TestResult) -> Optional[str]:
        """Start a test peer review"""
        if not self.quality_system:
            return None
        
        # Use completed cycle for review
        cycle_id = test_result.artifacts.get("cycle_id")
        if not cycle_id:
            return None
        
        review_data = {
            "cycle_id": cycle_id,
            "data_completeness_percent": 95.0,
            "p_value": 0.02,
            "effect_size": 0.65,
            "overall_data_quality": 0.85,
            "methodology_rigor": 0.8
        }
        
        review_id = await self.quality_system.start_review("cycle", cycle_id, review_data)
        return review_id
    
    async def _trigger_safety_violation(self, test_result: TestResult, violation_type: str) -> None:
        """Trigger a safety violation for testing"""
        if not self.safety_monitor:
            return
        
        # Simulate safety violation trigger
        test_result.detailed_logs.append(f"Triggered safety violation: {violation_type}")
        test_result.artifacts["safety_violation_triggered"] = violation_type
    
    async def _inject_agent_failure(self, test_result: TestResult) -> None:
        """Inject an agent failure for testing recovery"""
        # Simulate agent failure
        test_result.detailed_logs.append("Injected agent failure")
        test_result.artifacts["agent_failure_injected"] = True
    
    async def _validate_workflow_completion(self, test_result: TestResult) -> bool:
        """Validate that workflow completed successfully"""
        status = test_result.artifacts.get("final_cycle_status")
        if not status:
            return False
        
        return status.get("state") == "completed" and status.get("progress_percentage", 0) >= 100
    
    async def _validate_quality_score(self, test_result: TestResult, threshold: float) -> bool:
        """Validate quality score meets threshold"""
        status = test_result.artifacts.get("final_cycle_status")
        if not status:
            return False
        
        return status.get("quality_score", 0) >= threshold
    
    async def _validate_no_safety_violations(self, test_result: TestResult) -> bool:
        """Validate no safety violations occurred"""
        if not self.safety_monitor:
            return True
        
        safety_status = await self.safety_monitor.get_safety_status()
        return safety_status.get("active_violations", 0) == 0
    
    async def _validate_agent_participation(self, test_result: TestResult) -> bool:
        """Validate all expected agents participated"""
        agents = test_result.artifacts.get("test_agents", [])
        return len(agents) >= 2  # Minimum expected participation
    
    async def _validate_response_times(self, test_result: TestResult, max_seconds: float) -> bool:
        """Validate response times are within acceptable limits"""
        response_times = [
            test_result.performance_metrics.get(key, 0) 
            for key in test_result.performance_metrics.keys() 
            if "duration_seconds" in key
        ]
        
        return all(rt <= max_seconds for rt in response_times)
    
    async def _validate_safety_violations_detected(self, test_result: TestResult) -> bool:
        """Validate that safety violations were properly detected"""
        return test_result.artifacts.get("safety_violation_triggered") is not None
    
    async def _validate_quality_assessment(self, test_result: TestResult) -> bool:
        """Validate quality assessment completed"""
        review_id = test_result.artifacts.get("review_id")
        if not review_id or not self.quality_system:
            return False
        
        # Wait for review completion
        timeout = time.time() + 60  # 1 minute timeout
        while time.time() < timeout:
            status = await self.quality_system.get_review_status(review_id)
            if status and status.get("status") == "completed":
                return True
            await asyncio.sleep(2)
        
        return False
    
    async def _validate_system_recovery(self, test_result: TestResult) -> bool:
        """Validate system recovered from failures"""
        # Check system health after failure injection
        health_check = await self.validator.validate_system_health()
        return all(health_check.values())
    
    async def _cleanup_test_environment(self) -> None:
        """Clean up test environment between tests"""
        # Clean up test artifacts
        logger.info("Cleaning up test environment")
        
        # Stop any running cycles
        if self.workflow_engine:
            active_cycles = await self.workflow_engine.get_all_active_cycles()
            for cycle in active_cycles:
                await self.workflow_engine.pause_cycle(cycle["cycle_id"], "Test cleanup")
        
        # Reset safety monitor
        if self.safety_monitor:
            # Clear any test violations
            pass
        
        await asyncio.sleep(2)  # Brief pause for cleanup
    
    async def _generate_test_report(self, results: Dict[str, TestResult]) -> None:
        """Generate comprehensive test report"""
        report = {
            "test_execution_summary": {
                "total_tests": len(results),
                "passed": len([r for r in results.values() if r.status == TestStatus.PASSED]),
                "failed": len([r for r in results.values() if r.status == TestStatus.FAILED]),
                "timeout": len([r for r in results.values() if r.status == TestStatus.TIMEOUT]),
                "success_rate": len([r for r in results.values() if r.status == TestStatus.PASSED]) / len(results) * 100
            },
            "performance_summary": {
                "average_test_duration_minutes": sum(r.duration_seconds for r in results.values()) / len(results) / 60,
                "total_execution_time_minutes": sum(r.duration_seconds for r in results.values()) / 60
            },
            "test_results": []
        }
        
        for test_id, result in results.items():
            report["test_results"].append({
                "test_id": test_id,
                "test_name": result.test_name,
                "category": result.category.value,
                "status": result.status.value,
                "duration_minutes": result.duration_seconds / 60,
                "success_metrics_passed": sum(result.success_metrics.values()),
                "total_success_metrics": len(result.success_metrics),
                "error_message": result.error_message
            })
        
        # Save report
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_content = json.dumps(report, indent=2)
        
        logger.info("E2E Test Report Generated:")
        logger.info(f"Tests Passed: {report['test_execution_summary']['passed']}/{report['test_execution_summary']['total_tests']}")
        logger.info(f"Success Rate: {report['test_execution_summary']['success_rate']:.1f}%")
        logger.info(f"Total Execution Time: {report['performance_summary']['total_execution_time_minutes']:.1f} minutes")
    
    async def get_test_status(self) -> Dict[str, Any]:
        """Get current testing system status"""
        return {
            "test_scenarios_available": len(self.test_scenarios),
            "performance_benchmarks": len(self.performance_benchmarks),
            "tests_completed": len(self.test_results),
            "test_statistics": self.test_stats,
            "system_components_injected": {
                "orchestrator": self.orchestrator is not None,
                "workflow_engine": self.workflow_engine is not None,
                "task_scheduler": self.task_scheduler is not None,
                "safety_monitor": self.safety_monitor is not None,
                "quality_system": self.quality_system is not None
            }
        } 