"""
Workflow Engine - Autonomous Research Cycle Orchestration
Manages end-to-end research workflows with automated state transitions
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from core.research_project import ResearchProject, ResearchState, Priority
from core.orchestrator import ResearchOrchestrator
from communication.protocols import CollaborationProtocol, WorkflowStatus
from communication.message_bus import MessageBus, MessageType
from communication.agent_registry import AgentRegistry
from agents.agent_types import AgentType, AgentCapability

logger = logging.getLogger(__name__)

class WorkflowState(Enum):
    """States of automated workflow execution"""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    VALIDATING = "validating"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class WorkflowStep:
    """Individual step in a research workflow"""
    step_id: str
    step_name: str
    required_agent_type: AgentType
    required_capabilities: List[AgentCapability]
    input_requirements: List[str]
    output_deliverables: List[str]
    estimated_duration_minutes: int
    dependencies: List[str] = field(default_factory=list)
    is_completed: bool = False
    assigned_agent_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResearchWorkflowTemplate:
    """Template for automated research workflows"""
    template_id: str
    template_name: str
    description: str
    physics_domain: str
    steps: List[WorkflowStep]
    estimated_total_duration_hours: int
    success_criteria: List[str]
    failure_conditions: List[str]

@dataclass 
class AutomatedResearchCycle:
    """Complete automated research cycle instance"""
    cycle_id: str
    project_id: str
    template: ResearchWorkflowTemplate
    state: WorkflowState
    current_step_index: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    assigned_agents: Dict[str, str] = field(default_factory=dict)  # step_id -> agent_id
    step_results: Dict[str, Any] = field(default_factory=dict)
    safety_status: str = "safe"
    quality_score: float = 0.0
    intervention_required: bool = False

class WorkflowEngine:
    """
    Autonomous Research Workflow Engine
    
    Orchestrates complete research cycles from hypothesis to publication
    with minimal human intervention
    """
    
    def __init__(self, orchestrator: ResearchOrchestrator, 
                 collaboration_protocol: CollaborationProtocol,
                 agent_registry: AgentRegistry):
        self.orchestrator = orchestrator
        self.collaboration_protocol = collaboration_protocol
        self.agent_registry = agent_registry
        
        # Active workflows
        self.active_cycles: Dict[str, AutomatedResearchCycle] = {}
        self.workflow_templates: Dict[str, ResearchWorkflowTemplate] = {}
        
        # Execution settings
        self.max_concurrent_cycles = 5
        self.step_timeout_minutes = 60
        self.quality_threshold = 0.7
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "cycle_started": [],
            "step_completed": [],
            "cycle_completed": [],
            "cycle_failed": [],
            "intervention_required": []
        }
        
        # Initialize default templates
        self._initialize_workflow_templates()
    
    def _initialize_workflow_templates(self):
        """Initialize standard research workflow templates"""
        
        # Complete Physics Research Cycle
        physics_research_template = ResearchWorkflowTemplate(
            template_id="complete_physics_research",
            template_name="Complete Physics Research Cycle",
            description="End-to-end physics research from hypothesis to publication",
            physics_domain="general",
            steps=[
                WorkflowStep(
                    step_id="literature_review",
                    step_name="Literature Review and Background Research",
                    required_agent_type=AgentType.LITERATURE,
                    required_capabilities=[AgentCapability.LITERATURE_SEARCH, AgentCapability.KNOWLEDGE_SYNTHESIS],
                    input_requirements=["research_question", "physics_domain"],
                    output_deliverables=["literature_summary", "knowledge_gaps", "relevant_papers"],
                    estimated_duration_minutes=45
                ),
                WorkflowStep(
                    step_id="hypothesis_generation",
                    step_name="Hypothesis Generation and Theoretical Framework",
                    required_agent_type=AgentType.THEORY,
                    required_capabilities=[AgentCapability.HYPOTHESIS_GENERATION, AgentCapability.MATHEMATICAL_MODELING],
                    input_requirements=["literature_summary", "knowledge_gaps"],
                    output_deliverables=["hypothesis", "theoretical_framework", "predictions"],
                    estimated_duration_minutes=60,
                    dependencies=["literature_review"]
                ),
                WorkflowStep(
                    step_id="experimental_design",
                    step_name="Experimental Protocol Design",
                    required_agent_type=AgentType.EXPERIMENTAL,
                    required_capabilities=[AgentCapability.EXPERIMENTAL_DESIGN, AgentCapability.PROTOCOL_DEVELOPMENT],
                    input_requirements=["hypothesis", "theoretical_framework"],
                    output_deliverables=["experimental_protocol", "equipment_list", "measurement_plan"],
                    estimated_duration_minutes=90,
                    dependencies=["hypothesis_generation"]
                ),
                WorkflowStep(
                    step_id="safety_validation",
                    step_name="Safety Protocol Validation",
                    required_agent_type=AgentType.SAFETY,
                    required_capabilities=[AgentCapability.SAFETY_ASSESSMENT, AgentCapability.RISK_ANALYSIS],
                    input_requirements=["experimental_protocol", "equipment_list"],
                    output_deliverables=["safety_assessment", "risk_mitigation", "approval_status"],
                    estimated_duration_minutes=30,
                    dependencies=["experimental_design"]
                ),
                WorkflowStep(
                    step_id="data_collection",
                    step_name="Experimental Data Collection",
                    required_agent_type=AgentType.EXPERIMENTAL,
                    required_capabilities=[AgentCapability.DATA_COLLECTION, AgentCapability.INSTRUMENT_CONTROL],
                    input_requirements=["experimental_protocol", "safety_assessment"],
                    output_deliverables=["raw_data", "measurement_log", "experimental_conditions"],
                    estimated_duration_minutes=120,
                    dependencies=["safety_validation"]
                ),
                WorkflowStep(
                    step_id="data_analysis",
                    step_name="Statistical Analysis and Pattern Recognition",
                    required_agent_type=AgentType.ANALYSIS,
                    required_capabilities=[AgentCapability.DATA_ANALYSIS, AgentCapability.STATISTICAL_ANALYSIS],
                    input_requirements=["raw_data", "measurement_log"],
                    output_deliverables=["processed_data", "statistical_results", "visualizations"],
                    estimated_duration_minutes=75,
                    dependencies=["data_collection"]
                ),
                WorkflowStep(
                    step_id="result_interpretation",
                    step_name="Result Interpretation and Theory Validation",
                    required_agent_type=AgentType.THEORY,
                    required_capabilities=[AgentCapability.RESULT_INTERPRETATION, AgentCapability.THEORY_VALIDATION],
                    input_requirements=["processed_data", "statistical_results", "hypothesis"],
                    output_deliverables=["interpretation", "hypothesis_validation", "implications"],
                    estimated_duration_minutes=60,
                    dependencies=["data_analysis"]
                ),
                WorkflowStep(
                    step_id="peer_review",
                    step_name="Automated Peer Review and Quality Assessment",
                    required_agent_type=AgentType.META,
                    required_capabilities=[AgentCapability.PEER_REVIEW, AgentCapability.QUALITY_ASSESSMENT],
                    input_requirements=["interpretation", "methodology", "results"],
                    output_deliverables=["review_feedback", "quality_score", "publication_readiness"],
                    estimated_duration_minutes=45,
                    dependencies=["result_interpretation"]
                ),
                WorkflowStep(
                    step_id="report_generation",
                    step_name="Research Report and Publication Preparation",
                    required_agent_type=AgentType.META,
                    required_capabilities=[AgentCapability.REPORT_GENERATION, AgentCapability.SCIENTIFIC_WRITING],
                    input_requirements=["all_previous_outputs"],
                    output_deliverables=["research_report", "publication_draft", "supplementary_materials"],
                    estimated_duration_minutes=90,
                    dependencies=["peer_review"]
                )
            ],
            estimated_total_duration_hours=9,
            success_criteria=[
                "All steps completed successfully",
                "Quality score >= 0.7",
                "Peer review approval",
                "Safety validation passed",
                "Statistical significance achieved"
            ],
            failure_conditions=[
                "Safety violation detected",
                "Quality score < 0.5",
                "Critical step failure",
                "Resource constraints exceeded",
                "Timeout exceeded"
            ]
        )
        
        self.workflow_templates["complete_physics_research"] = physics_research_template
        
        # Quick Validation Cycle (for testing and rapid iteration)
        quick_validation_template = ResearchWorkflowTemplate(
            template_id="quick_validation",
            template_name="Quick Hypothesis Validation",
            description="Rapid validation cycle for quick hypothesis testing",
            physics_domain="general",
            steps=[
                WorkflowStep(
                    step_id="hypothesis_check",
                    step_name="Hypothesis Literature Check",
                    required_agent_type=AgentType.LITERATURE,
                    required_capabilities=[AgentCapability.LITERATURE_SEARCH],
                    input_requirements=["hypothesis"],
                    output_deliverables=["literature_check", "novelty_assessment"],
                    estimated_duration_minutes=15
                ),
                WorkflowStep(
                    step_id="quick_experiment",
                    step_name="Quick Experimental Validation",
                    required_agent_type=AgentType.EXPERIMENTAL,
                    required_capabilities=[AgentCapability.EXPERIMENTAL_DESIGN, AgentCapability.DATA_COLLECTION],
                    input_requirements=["hypothesis", "literature_check"],
                    output_deliverables=["experimental_results", "validation_status"],
                    estimated_duration_minutes=30,
                    dependencies=["hypothesis_check"]
                ),
                WorkflowStep(
                    step_id="quick_analysis",
                    step_name="Rapid Result Analysis",
                    required_agent_type=AgentType.ANALYSIS,
                    required_capabilities=[AgentCapability.DATA_ANALYSIS],
                    input_requirements=["experimental_results"],
                    output_deliverables=["analysis_summary", "recommendation"],
                    estimated_duration_minutes=15,
                    dependencies=["quick_experiment"]
                )
            ],
            estimated_total_duration_hours=1,
            success_criteria=[
                "Hypothesis validated or refuted",
                "Results statistically significant",
                "No safety violations"
            ],
            failure_conditions=[
                "Safety violation",
                "Inconclusive results",
                "Agent failure"
            ]
        )
        
        self.workflow_templates["quick_validation"] = quick_validation_template
        
        logger.info(f"Initialized {len(self.workflow_templates)} workflow templates")
    
    async def start_automated_cycle(self, project: ResearchProject, 
                                  template_id: str = "complete_physics_research") -> Optional[str]:
        """Start an automated research cycle for a project"""
        try:
            if len(self.active_cycles) >= self.max_concurrent_cycles:
                logger.warning("Maximum concurrent cycles reached, queuing request")
                return None
            
            if template_id not in self.workflow_templates:
                logger.error(f"Unknown workflow template: {template_id}")
                return None
            
            template = self.workflow_templates[template_id]
            cycle_id = str(uuid4())
            
            # Create automated research cycle
            cycle = AutomatedResearchCycle(
                cycle_id=cycle_id,
                project_id=project.id,
                template=template,
                state=WorkflowState.INITIALIZED,
                current_step_index=0,
                created_at=datetime.utcnow()
            )
            
            self.active_cycles[cycle_id] = cycle
            
            # Start the execution
            asyncio.create_task(self._execute_research_cycle(cycle))
            
            await self._trigger_event("cycle_started", cycle)
            logger.info(f"Started automated research cycle {cycle_id} for project {project.id}")
            
            return cycle_id
            
        except Exception as e:
            logger.error(f"Failed to start automated cycle: {e}")
            return None
    
    async def _execute_research_cycle(self, cycle: AutomatedResearchCycle) -> None:
        """Execute a complete automated research cycle"""
        try:
            cycle.state = WorkflowState.PLANNING
            cycle.started_at = datetime.utcnow()
            
            # Phase 1: Planning and Agent Assignment
            planning_success = await self._plan_workflow_execution(cycle)
            if not planning_success:
                await self._fail_cycle(cycle, "Planning phase failed")
                return
            
            # Phase 2: Execute workflow steps
            cycle.state = WorkflowState.EXECUTING
            execution_success = await self._execute_workflow_steps(cycle)
            if not execution_success:
                await self._fail_cycle(cycle, "Execution phase failed")
                return
            
            # Phase 3: Validation and Quality Check
            cycle.state = WorkflowState.VALIDATING
            validation_success = await self._validate_workflow_results(cycle)
            if not validation_success:
                await self._fail_cycle(cycle, "Validation phase failed")
                return
            
            # Phase 4: Completion
            cycle.state = WorkflowState.COMPLETING
            await self._complete_cycle(cycle)
            
        except Exception as e:
            logger.error(f"Error executing research cycle {cycle.cycle_id}: {e}")
            await self._fail_cycle(cycle, f"Unexpected error: {e}")
    
    async def _plan_workflow_execution(self, cycle: AutomatedResearchCycle) -> bool:
        """Plan the workflow execution and assign agents"""
        try:
            # Assign agents to each step
            for step in cycle.template.steps:
                # Find best agent for this step
                available_agents = await self.agent_registry.find_agents_by_capability(
                    step.required_capabilities,
                    step.required_agent_type
                )
                
                if not available_agents:
                    logger.error(f"No available agents for step {step.step_id}")
                    return False
                
                # Select best agent (first one for now, could be more sophisticated)
                selected_agent = available_agents[0]
                cycle.assigned_agents[step.step_id] = selected_agent["agent_id"]
                
                logger.info(f"Assigned agent {selected_agent['agent_id']} to step {step.step_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Planning failed for cycle {cycle.cycle_id}: {e}")
            return False
    
    async def _execute_workflow_steps(self, cycle: AutomatedResearchCycle) -> bool:
        """Execute all workflow steps in the correct order"""
        try:
            for i, step in enumerate(cycle.template.steps):
                cycle.current_step_index = i
                
                # Check dependencies
                if not await self._check_step_dependencies(cycle, step):
                    logger.error(f"Dependencies not met for step {step.step_id}")
                    return False
                
                # Execute the step
                step_success = await self._execute_workflow_step(cycle, step)
                if not step_success:
                    logger.error(f"Step {step.step_id} failed")
                    return False
                
                # Update progress
                cycle.progress_percentage = ((i + 1) / len(cycle.template.steps)) * 100
                await self._trigger_event("step_completed", {"cycle": cycle, "step": step})
            
            return True
            
        except Exception as e:
            logger.error(f"Step execution failed for cycle {cycle.cycle_id}: {e}")
            return False
    
    async def _execute_workflow_step(self, cycle: AutomatedResearchCycle, step: WorkflowStep) -> bool:
        """Execute a single workflow step"""
        try:
            step.started_at = datetime.utcnow()
            assigned_agent_id = cycle.assigned_agents[step.step_id]
            
            # Prepare input data
            input_data = await self._prepare_step_input_data(cycle, step)
            
            # Create collaboration workflow for this step
            workflow_id = await self.collaboration_protocol.start_workflow(
                "single_step_execution",
                [assigned_agent_id],
                {
                    "step_definition": step.__dict__,
                    "input_data": input_data,
                    "cycle_context": {
                        "cycle_id": cycle.cycle_id,
                        "project_id": cycle.project_id
                    }
                }
            )
            
            if not workflow_id:
                return False
            
            # Monitor step execution
            success = await self._monitor_step_execution(workflow_id, step)
            
            if success:
                step.is_completed = True
                step.completed_at = datetime.utcnow()
                
                # Store results
                workflow_status = await self.collaboration_protocol.get_workflow_status(workflow_id)
                if workflow_status and workflow_status.get("results"):
                    step.results = workflow_status["results"]
                    cycle.step_results[step.step_id] = step.results
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing step {step.step_id}: {e}")
            return False
    
    async def _monitor_step_execution(self, workflow_id: str, step: WorkflowStep) -> bool:
        """Monitor the execution of a workflow step"""
        timeout = datetime.utcnow() + timedelta(minutes=step.estimated_duration_minutes * 2)
        
        while datetime.utcnow() < timeout:
            status = await self.collaboration_protocol.get_workflow_status(workflow_id)
            
            if not status:
                await asyncio.sleep(5)
                continue
            
            if status["status"] == WorkflowStatus.COMPLETED.value:
                return True
            elif status["status"] == WorkflowStatus.FAILED.value:
                return False
            
            await asyncio.sleep(10)  # Check every 10 seconds
        
        logger.warning(f"Step {step.step_id} timed out")
        return False
    
    async def _prepare_step_input_data(self, cycle: AutomatedResearchCycle, step: WorkflowStep) -> Dict[str, Any]:
        """Prepare input data for a workflow step"""
        input_data = {}
        
        # Get project data
        project = await self.orchestrator.get_project(cycle.project_id)
        if project:
            input_data.update({
                "research_question": project.research_question,
                "hypothesis": project.hypothesis,
                "physics_domain": project.physics_domain,
                "project_context": project.metadata
            })
        
        # Add results from previous steps
        for requirement in step.input_requirements:
            if requirement in cycle.step_results:
                input_data[requirement] = cycle.step_results[requirement]
            
            # Check if requirement matches output from previous steps
            for prev_step_id, results in cycle.step_results.items():
                if isinstance(results, dict) and requirement in results:
                    input_data[requirement] = results[requirement]
        
        return input_data
    
    async def _check_step_dependencies(self, cycle: AutomatedResearchCycle, step: WorkflowStep) -> bool:
        """Check if all dependencies for a step are satisfied"""
        for dependency in step.dependencies:
            # Find the dependent step
            dependent_step = None
            for s in cycle.template.steps:
                if s.step_id == dependency:
                    dependent_step = s
                    break
            
            if not dependent_step or not dependent_step.is_completed:
                return False
        
        return True
    
    async def _validate_workflow_results(self, cycle: AutomatedResearchCycle) -> bool:
        """Validate the results of the complete workflow"""
        try:
            # Check if all success criteria are met
            success_count = 0
            total_criteria = len(cycle.template.success_criteria)
            
            for criteria in cycle.template.success_criteria:
                if await self._check_success_criteria(cycle, criteria):
                    success_count += 1
            
            # Calculate quality score
            cycle.quality_score = success_count / total_criteria if total_criteria > 0 else 0.0
            
            # Check quality threshold
            if cycle.quality_score >= self.quality_threshold:
                logger.info(f"Cycle {cycle.cycle_id} passed validation with quality score {cycle.quality_score}")
                return True
            else:
                logger.warning(f"Cycle {cycle.cycle_id} failed validation with quality score {cycle.quality_score}")
                return False
            
        except Exception as e:
            logger.error(f"Validation failed for cycle {cycle.cycle_id}: {e}")
            return False
    
    async def _check_success_criteria(self, cycle: AutomatedResearchCycle, criteria: str) -> bool:
        """Check if a specific success criteria is met"""
        # Simplified criteria checking - in real implementation would be more sophisticated
        criteria_checks = {
            "All steps completed successfully": all(step.is_completed for step in cycle.template.steps),
            "Quality score >= 0.7": cycle.quality_score >= 0.7,
            "Peer review approval": cycle.step_results.get("peer_review", {}).get("approval", False),
            "Safety validation passed": cycle.step_results.get("safety_validation", {}).get("approval_status", "") == "approved",
            "Statistical significance achieved": cycle.step_results.get("data_analysis", {}).get("statistical_significance", False),
            "Hypothesis validated or refuted": "hypothesis_validation" in cycle.step_results.get("result_interpretation", {}),
            "Results statistically significant": cycle.step_results.get("quick_analysis", {}).get("statistical_significance", False),
            "No safety violations": cycle.safety_status == "safe"
        }
        
        return criteria_checks.get(criteria, False)
    
    async def _complete_cycle(self, cycle: AutomatedResearchCycle) -> None:
        """Complete a successful research cycle"""
        cycle.state = WorkflowState.COMPLETED
        cycle.completed_at = datetime.utcnow()
        
        # Update the associated project
        project = await self.orchestrator.get_project(cycle.project_id)
        if project:
            project.update_state(ResearchState.COMPLETED, f"Automated cycle {cycle.cycle_id} completed")
            project.results.update({
                "automated_cycle_results": cycle.step_results,
                "quality_score": cycle.quality_score,
                "cycle_duration": (cycle.completed_at - cycle.started_at).total_seconds() / 3600
            })
        
        await self._trigger_event("cycle_completed", cycle)
        logger.info(f"Successfully completed research cycle {cycle.cycle_id}")
    
    async def _fail_cycle(self, cycle: AutomatedResearchCycle, reason: str) -> None:
        """Handle cycle failure"""
        cycle.state = WorkflowState.FAILED
        cycle.completed_at = datetime.utcnow()
        
        # Update the associated project
        project = await self.orchestrator.get_project(cycle.project_id)
        if project:
            project.update_state(ResearchState.FAILED, f"Automated cycle failed: {reason}")
        
        await self._trigger_event("cycle_failed", {"cycle": cycle, "reason": reason})
        logger.error(f"Research cycle {cycle.cycle_id} failed: {reason}")
    
    async def _trigger_event(self, event_type: str, data: Any) -> None:
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def get_cycle_status(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an automated research cycle"""
        cycle = self.active_cycles.get(cycle_id)
        if not cycle:
            return None
        
        return {
            "cycle_id": cycle.cycle_id,
            "project_id": cycle.project_id,
            "template_name": cycle.template.template_name,
            "state": cycle.state.value,
            "progress_percentage": cycle.progress_percentage,
            "current_step": cycle.current_step_index,
            "total_steps": len(cycle.template.steps),
            "quality_score": cycle.quality_score,
            "safety_status": cycle.safety_status,
            "created_at": cycle.created_at.isoformat(),
            "started_at": cycle.started_at.isoformat() if cycle.started_at else None,
            "completed_at": cycle.completed_at.isoformat() if cycle.completed_at else None,
            "assigned_agents": cycle.assigned_agents,
            "intervention_required": cycle.intervention_required
        }
    
    async def pause_cycle(self, cycle_id: str, reason: str = "") -> bool:
        """Pause an active research cycle"""
        cycle = self.active_cycles.get(cycle_id)
        if not cycle or cycle.state in [WorkflowState.COMPLETED, WorkflowState.FAILED]:
            return False
        
        cycle.state = WorkflowState.PAUSED
        logger.info(f"Paused research cycle {cycle_id}: {reason}")
        return True
    
    async def resume_cycle(self, cycle_id: str) -> bool:
        """Resume a paused research cycle"""
        cycle = self.active_cycles.get(cycle_id)
        if not cycle or cycle.state != WorkflowState.PAUSED:
            return False
        
        cycle.state = WorkflowState.EXECUTING
        asyncio.create_task(self._execute_research_cycle(cycle))
        logger.info(f"Resumed research cycle {cycle_id}")
        return True
    
    async def get_all_active_cycles(self) -> List[Dict[str, Any]]:
        """Get status of all active research cycles"""
        cycles = []
        for cycle_id in self.active_cycles:
            status = await self.get_cycle_status(cycle_id)
            if status:
                cycles.append(status)
        return cycles
    
    async def cleanup_completed_cycles(self) -> None:
        """Clean up completed and failed cycles"""
        to_remove = []
        for cycle_id, cycle in self.active_cycles.items():
            if cycle.state in [WorkflowState.COMPLETED, WorkflowState.FAILED]:
                # Keep cycles for 24 hours after completion for debugging
                if cycle.completed_at and (datetime.utcnow() - cycle.completed_at).total_seconds() > 86400:
                    to_remove.append(cycle_id)
        
        for cycle_id in to_remove:
            del self.active_cycles[cycle_id]
            logger.info(f"Cleaned up completed cycle {cycle_id}") 