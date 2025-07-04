"""
Research Orchestrator for Phase 6 - Autonomous Research
Intelligent task decomposition and multi-agent coordination
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .advanced_llm import AdvancedLLMManager, TaskType, ResearchContext

class ResearchStage(Enum):
    """Stages of the research process"""
    QUESTION_ANALYSIS = "question_analysis"
    LITERATURE_REVIEW = "literature_review"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EXPERIMENTAL_DESIGN = "experimental_design"
    SIMULATION_EXECUTION = "simulation_execution"
    DATA_ANALYSIS = "data_analysis"
    PEER_REVIEW = "peer_review"
    REPORT_GENERATION = "report_generation"
    PUBLICATION_PREP = "publication_prep"

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ResearchTask:
    """Individual research task within a larger project"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    stage: ResearchStage = ResearchStage.QUESTION_ANALYSIS
    task_type: TaskType = TaskType.REASONING
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(hours=1))
    estimated_cost: float = 100.0
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResearchProject:
    """Complete research project with multiple tasks"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    research_question: str = ""
    domain: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    budget: float = 50000.0
    budget_used: float = 0.0
    tasks: List[ResearchTask] = field(default_factory=list)
    status: str = "planning"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    findings: List[str] = field(default_factory=list)
    final_report: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ResearchOrchestrator:
    """
    Orchestrates autonomous research by decomposing complex questions
    into manageable tasks and coordinating multiple AI agents
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_manager = AdvancedLLMManager()
        
        # Active projects and tasks
        self.active_projects: Dict[str, ResearchProject] = {}
        self.completed_projects: Dict[str, ResearchProject] = {}
        
        # Agent specializations
        self.agent_specializations = {
            'theory_agent': [TaskType.REASONING, TaskType.MATHEMATICAL, TaskType.HYPOTHESIS],
            'experimental_agent': [TaskType.EXPERIMENTAL, TaskType.ANALYSIS],
            'literature_agent': [TaskType.LITERATURE],
            'analysis_agent': [TaskType.ANALYSIS, TaskType.CODING],
            'safety_agent': [TaskType.SAFETY],
            'meta_agent': [TaskType.REASONING, TaskType.LITERATURE]
        }
        
        # Agent availability
        self.agent_status = {
            'theory_agent': 'available',
            'experimental_agent': 'available',
            'literature_agent': 'available', 
            'analysis_agent': 'available',
            'safety_agent': 'available',
            'meta_agent': 'available'
        }
        
    async def create_research_project(self, 
                                    research_question: str,
                                    domain: str,
                                    budget: float = 50000.0,
                                    priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """
        Create a new research project and decompose it into tasks
        """
        try:
            # Create project
            project = ResearchProject(
                title=f"Research: {research_question[:50]}...",
                research_question=research_question,
                domain=domain,
                budget=budget,
                priority=priority
            )
            
            # Decompose into tasks
            tasks = await self._decompose_research_question(
                research_question, domain, budget
            )
            
            project.tasks = tasks
            
            # Assign agents to tasks
            await self._assign_agents_to_tasks(project)
            
            # Store project
            self.active_projects[project.id] = project
            
            self.logger.info(f"Created research project: {project.id} with {len(tasks)} tasks")
            
            return project.id
            
        except Exception as e:
            self.logger.error(f"Error creating research project: {str(e)}")
            raise
    
    async def _decompose_research_question(self, 
                                         research_question: str,
                                         domain: str, 
                                         budget: float) -> List[ResearchTask]:
        """
        Use AI to decompose a complex research question into manageable tasks
        """
        context = ResearchContext(
            domain=domain,
            topic=research_question,
            previous_findings=[],
            constraints={"budget": budget},
            priority="high",
            budget_remaining=budget
        )
        
        decomposition_prompt = f"""
        Decompose this research question into a comprehensive research plan: "{research_question}"
        
        Create a detailed task breakdown that covers:
        1. Question analysis and scope definition
        2. Literature review and background research
        3. Hypothesis generation
        4. Experimental design (if applicable)
        5. Data collection/simulation planning
        6. Analysis methodology
        7. Peer review and validation
        8. Report generation
        
        For each task, specify:
        - Clear title and description
        - Estimated duration (hours)
        - Estimated cost
        - Dependencies on other tasks
        - Required expertise/agent type
        - Expected deliverables
        
        Format as a structured list that can guide autonomous execution.
        """
        
        response = await self.llm_manager.route_task(
            TaskType.REASONING, decomposition_prompt, context
        )
        
        # Parse response into tasks
        tasks = self._parse_task_breakdown(response.content, domain)
        
        return tasks
    
    def _parse_task_breakdown(self, task_breakdown: str, domain: str) -> List[ResearchTask]:
        """
        Parse the AI-generated task breakdown into ResearchTask objects
        """
        tasks = []
        
        # This is a simplified parser - in production, would use more sophisticated NLP
        task_sections = task_breakdown.split('\n')
        current_task = None
        
        for line in task_sections:
            line = line.strip()
            if not line:
                continue
                
            # Look for task indicators
            if any(indicator in line.lower() for indicator in ['task:', 'step:', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.']):
                if current_task:
                    tasks.append(current_task)
                
                # Extract task title
                title = line
                for prefix in ['task:', 'step:', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.']:
                    title = title.replace(prefix, '').strip()
                
                # Determine stage and task type
                stage, task_type = self._determine_task_stage_and_type(title)
                
                current_task = ResearchTask(
                    title=title[:100],  # Limit title length
                    description=title,
                    stage=stage,
                    task_type=task_type,
                    priority=TaskPriority.MEDIUM,
                    estimated_duration=timedelta(hours=2),  # Default
                    estimated_cost=500.0  # Default
                )
            
            elif current_task and ('duration:' in line.lower() or 'time:' in line.lower()):
                # Extract duration
                try:
                    hours = float(''.join(filter(str.isdigit, line)))
                    current_task.estimated_duration = timedelta(hours=max(1, hours))
                except:
                    pass
            
            elif current_task and ('cost:' in line.lower() or '$' in line):
                # Extract cost
                try:
                    cost = float(''.join(filter(lambda x: x.isdigit() or x == '.', line)))
                    current_task.estimated_cost = max(50.0, cost)
                except:
                    pass
        
        if current_task:
            tasks.append(current_task)
        
        # If no tasks were parsed, create default research workflow
        if not tasks:
            tasks = self._create_default_research_workflow(domain)
        
        return tasks
    
    def _determine_task_stage_and_type(self, title: str) -> Tuple[ResearchStage, TaskType]:
        """Determine the research stage and task type from task title"""
        title_lower = title.lower()
        
        # Stage mapping
        if any(keyword in title_lower for keyword in ['literature', 'review', 'background']):
            return ResearchStage.LITERATURE_REVIEW, TaskType.LITERATURE
        elif any(keyword in title_lower for keyword in ['hypothesis', 'theory', 'predict']):
            return ResearchStage.HYPOTHESIS_GENERATION, TaskType.HYPOTHESIS
        elif any(keyword in title_lower for keyword in ['experiment', 'design', 'methodology']):
            return ResearchStage.EXPERIMENTAL_DESIGN, TaskType.EXPERIMENTAL
        elif any(keyword in title_lower for keyword in ['simulation', 'model', 'compute']):
            return ResearchStage.SIMULATION_EXECUTION, TaskType.CODING
        elif any(keyword in title_lower for keyword in ['analysis', 'data', 'statistical']):
            return ResearchStage.DATA_ANALYSIS, TaskType.ANALYSIS
        elif any(keyword in title_lower for keyword in ['review', 'validate', 'check']):
            return ResearchStage.PEER_REVIEW, TaskType.SAFETY
        elif any(keyword in title_lower for keyword in ['report', 'write', 'document']):
            return ResearchStage.REPORT_GENERATION, TaskType.LITERATURE
        else:
            return ResearchStage.QUESTION_ANALYSIS, TaskType.REASONING
    
    def _create_default_research_workflow(self, domain: str) -> List[ResearchTask]:
        """Create a default research workflow if parsing fails"""
        return [
            ResearchTask(
                title="Research Question Analysis",
                description="Analyze and refine the research question",
                stage=ResearchStage.QUESTION_ANALYSIS,
                task_type=TaskType.REASONING,
                estimated_duration=timedelta(hours=2),
                estimated_cost=200.0
            ),
            ResearchTask(
                title="Literature Review",
                description="Comprehensive review of existing literature",
                stage=ResearchStage.LITERATURE_REVIEW,
                task_type=TaskType.LITERATURE,
                estimated_duration=timedelta(hours=6),
                estimated_cost=800.0
            ),
            ResearchTask(
                title="Hypothesis Generation",
                description="Generate testable hypotheses",
                stage=ResearchStage.HYPOTHESIS_GENERATION,
                task_type=TaskType.HYPOTHESIS,
                estimated_duration=timedelta(hours=3),
                estimated_cost=400.0,
                dependencies=["Literature Review"]
            ),
            ResearchTask(
                title="Experimental Design",
                description="Design experiments to test hypotheses",
                stage=ResearchStage.EXPERIMENTAL_DESIGN,
                task_type=TaskType.EXPERIMENTAL,
                estimated_duration=timedelta(hours=4),
                estimated_cost=600.0,
                dependencies=["Hypothesis Generation"]
            ),
            ResearchTask(
                title="Data Analysis",
                description="Analyze collected data and results",
                stage=ResearchStage.DATA_ANALYSIS,
                task_type=TaskType.ANALYSIS,
                estimated_duration=timedelta(hours=5),
                estimated_cost=700.0,
                dependencies=["Experimental Design"]
            ),
            ResearchTask(
                title="Report Generation",
                description="Generate comprehensive research report",
                stage=ResearchStage.REPORT_GENERATION,
                task_type=TaskType.LITERATURE,
                estimated_duration=timedelta(hours=4),
                estimated_cost=500.0,
                dependencies=["Data Analysis"]
            )
        ]
    
    async def _assign_agents_to_tasks(self, project: ResearchProject):
        """Assign the most suitable agents to each task"""
        for task in project.tasks:
            best_agent = self._find_best_agent_for_task(task)
            if best_agent:
                task.assigned_agent = best_agent
                self.logger.info(f"Assigned {best_agent} to task: {task.title}")
    
    def _find_best_agent_for_task(self, task: ResearchTask) -> Optional[str]:
        """Find the best available agent for a specific task"""
        suitable_agents = []
        
        for agent, specializations in self.agent_specializations.items():
            if task.task_type in specializations and self.agent_status[agent] == 'available':
                suitable_agents.append(agent)
        
        # For now, return the first suitable agent
        # In production, would consider workload, performance history, etc.
        return suitable_agents[0] if suitable_agents else None
    
    async def start_project(self, project_id: str) -> bool:
        """Start execution of a research project"""
        if project_id not in self.active_projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.active_projects[project_id]
        project.status = "executing"
        project.started_at = datetime.now()
        
        # Start executing tasks
        await self._execute_project_tasks(project)
        
        return True
    
    async def _execute_project_tasks(self, project: ResearchProject):
        """Execute all tasks in a project, respecting dependencies"""
        completed_tasks = set()
        
        while len(completed_tasks) < len(project.tasks):
            # Find ready tasks (no pending dependencies)
            ready_tasks = [
                task for task in project.tasks 
                if task.status == "pending" and 
                all(dep in completed_tasks for dep in task.dependencies)
            ]
            
            if not ready_tasks:
                break  # No more tasks can be started
            
            # Execute ready tasks in parallel
            await asyncio.gather(*[
                self._execute_task(task, project) 
                for task in ready_tasks[:3]  # Limit parallel execution
            ])
            
            # Update completed tasks
            for task in ready_tasks:
                if task.status == "completed":
                    completed_tasks.add(task.title)
        
        # Update project status
        if len(completed_tasks) == len(project.tasks):
            project.status = "completed"
            project.completed_at = datetime.now()
            await self._generate_final_report(project)
    
    async def _execute_task(self, task: ResearchTask, project: ResearchProject):
        """Execute an individual research task"""
        try:
            task.status = "executing"
            task.started_at = datetime.now()
            
            # Create context for the task
            context = ResearchContext(
                domain=project.domain,
                topic=f"{project.research_question} - {task.title}",
                previous_findings=project.findings,
                constraints={"budget_remaining": project.budget - project.budget_used},
                priority=project.priority.value,
                budget_remaining=project.budget - project.budget_used
            )
            
            # Execute the task using the appropriate LLM
            response = await self.llm_manager.route_task(
                task.task_type, 
                task.description, 
                context
            )
            
            # Store results
            task.results = {
                'content': response.content,
                'confidence': response.confidence,
                'reasoning': response.reasoning,
                'sources': response.sources,
                'cost': response.cost
            }
            
            # Update project budget
            project.budget_used += response.cost
            
            # Add findings
            if response.content:
                project.findings.append(f"{task.title}: {response.content[:200]}...")
            
            task.status = "completed"
            task.completed_at = datetime.now()
            
            self.logger.info(f"Completed task: {task.title}")
            
        except Exception as e:
            task.status = "failed"
            task.results = {'error': str(e)}
            self.logger.error(f"Task failed: {task.title} - {str(e)}")
    
    async def _generate_final_report(self, project: ResearchProject):
        """Generate a comprehensive final report for the project"""
        try:
            context = ResearchContext(
                domain=project.domain,
                topic=project.research_question,
                previous_findings=project.findings,
                constraints={},
                priority="high",
                budget_remaining=0.0
            )
            
            report_prompt = f"""
            Generate a comprehensive research report for this project:
            
            Research Question: {project.research_question}
            Domain: {project.domain}
            
            Key Findings:
            {chr(10).join(project.findings)}
            
            Include:
            1. Executive Summary
            2. Research Methodology
            3. Key Findings and Results
            4. Analysis and Interpretation
            5. Conclusions and Implications
            6. Future Research Directions
            7. Limitations and Considerations
            
            Format as a professional research report.
            """
            
            response = await self.llm_manager.route_task(
                TaskType.LITERATURE, report_prompt, context
            )
            
            project.final_report = response.content
            project.budget_used += response.cost
            
            self.logger.info(f"Generated final report for project: {project.id}")
            
        except Exception as e:
            self.logger.error(f"Error generating final report: {str(e)}")
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get detailed status of a research project"""
        if project_id in self.active_projects:
            project = self.active_projects[project_id]
        elif project_id in self.completed_projects:
            project = self.completed_projects[project_id]
        else:
            raise ValueError(f"Project {project_id} not found")
        
        return {
            'project_id': project.id,
            'title': project.title,
            'status': project.status,
            'progress': self._calculate_progress(project),
            'tasks_completed': len([t for t in project.tasks if t.status == "completed"]),
            'total_tasks': len(project.tasks),
            'budget_used': project.budget_used,
            'budget_total': project.budget,
            'findings_count': len(project.findings),
            'created_at': project.created_at,
            'started_at': project.started_at,
            'completed_at': project.completed_at
        }
    
    def _calculate_progress(self, project: ResearchProject) -> float:
        """Calculate project completion progress"""
        if not project.tasks:
            return 0.0
        
        completed = len([t for t in project.tasks if t.status == "completed"])
        return (completed / len(project.tasks)) * 100.0
    
    def get_all_projects(self) -> Dict[str, Any]:
        """Get summary of all projects"""
        return {
            'active_projects': [self.get_project_status(pid) for pid in self.active_projects.keys()],
            'completed_projects': [self.get_project_status(pid) for pid in self.completed_projects.keys()],
            'agent_status': self.agent_status,
            'total_budget_used': sum(p.budget_used for p in self.active_projects.values()) + 
                               sum(p.budget_used for p in self.completed_projects.values())
        } 