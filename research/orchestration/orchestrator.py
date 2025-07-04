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

import sys
sys.path.append('../..')
from research.advanced_llm import AdvancedLLMManager, TaskType, ResearchContext

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
            
            # For demo, create a simplified task structure
            project.tasks = self._create_demo_research_workflow(domain, research_question)
            
            # Assign agents to tasks
            await self._assign_agents_to_tasks(project)
            
            # Store project
            self.active_projects[project.id] = project
            
            self.logger.info(f"Created research project: {project.id} with {len(project.tasks)} tasks")
            
            return project.id
            
        except Exception as e:
            self.logger.error(f"Error creating research project: {str(e)}")
            raise
    
    def _create_demo_research_workflow(self, domain: str, research_question: str) -> List[ResearchTask]:
        """Create a demo research workflow for immediate functionality"""
        return [
            ResearchTask(
                title="Research Question Analysis",
                description=f"Analyze and refine: {research_question}",
                stage=ResearchStage.QUESTION_ANALYSIS,
                task_type=TaskType.REASONING,
                estimated_duration=timedelta(hours=2),
                estimated_cost=200.0,
                status="pending"
            ),
            ResearchTask(
                title="Literature Review",
                description=f"Comprehensive review of {domain} literature",
                stage=ResearchStage.LITERATURE_REVIEW,
                task_type=TaskType.LITERATURE,
                estimated_duration=timedelta(hours=6),
                estimated_cost=800.0,
                dependencies=["Research Question Analysis"],
                status="pending"
            ),
            ResearchTask(
                title="Hypothesis Generation",
                description="Generate testable hypotheses",
                stage=ResearchStage.HYPOTHESIS_GENERATION,
                task_type=TaskType.HYPOTHESIS,
                estimated_duration=timedelta(hours=3),
                estimated_cost=400.0,
                dependencies=["Literature Review"],
                status="pending"
            ),
            ResearchTask(
                title="Experimental Design",
                description="Design experiments to test hypotheses",
                stage=ResearchStage.EXPERIMENTAL_DESIGN,
                task_type=TaskType.EXPERIMENTAL,
                estimated_duration=timedelta(hours=4),
                estimated_cost=600.0,
                dependencies=["Hypothesis Generation"],
                status="pending"
            ),
            ResearchTask(
                title="Data Analysis",
                description="Analyze collected data and results",
                stage=ResearchStage.DATA_ANALYSIS,
                task_type=TaskType.ANALYSIS,
                estimated_duration=timedelta(hours=5),
                estimated_cost=700.0,
                dependencies=["Experimental Design"],
                status="pending"
            ),
            ResearchTask(
                title="Report Generation",
                description="Generate comprehensive research report",
                stage=ResearchStage.REPORT_GENERATION,
                task_type=TaskType.LITERATURE,
                estimated_duration=timedelta(hours=4),
                estimated_cost=500.0,
                dependencies=["Data Analysis"],
                status="pending"
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
        
        return suitable_agents[0] if suitable_agents else None
    
    async def start_project(self, project_id: str) -> bool:
        """Start execution of a research project"""
        if project_id not in self.active_projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.active_projects[project_id]
        project.status = "executing"
        project.started_at = datetime.now()
        
        # For demo, simulate task progression
        await self._simulate_project_execution(project)
        
        return True
    
    async def _simulate_project_execution(self, project: ResearchProject):
        """Simulate project execution for demo purposes"""
        import random
        
        for i, task in enumerate(project.tasks):
            # Simulate task execution
            task.status = "executing"
            task.started_at = datetime.now()
            
            # Simulate some processing time
            await asyncio.sleep(0.5)
            
            # Add some demo results
            task.results = {
                'content': f"Completed {task.title} for {project.domain} research",
                'confidence': random.uniform(0.7, 0.95),
                'reasoning': f"Applied {task.task_type.value} methodology",
                'sources': [f"Source {i+1}", f"Reference {i+1}"],
                'cost': task.estimated_cost * random.uniform(0.8, 1.2)
            }
            
            project.budget_used += task.results['cost']
            project.findings.append(f"{task.title}: Completed successfully")
            
            task.status = "completed"
            task.completed_at = datetime.now()
        
        project.status = "completed"
        project.completed_at = datetime.now()
        project.final_report = f"Research on '{project.research_question}' completed successfully with {len(project.findings)} key findings."
    
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
            'research_question': project.research_question,
            'domain': project.domain,
            'status': project.status,
            'progress': self._calculate_progress(project),
            'tasks_completed': len([t for t in project.tasks if t.status == "completed"]),
            'total_tasks': len(project.tasks),
            'budget_used': project.budget_used,
            'budget_total': project.budget,
            'findings_count': len(project.findings),
            'created_at': project.created_at,
            'started_at': project.started_at,
            'completed_at': project.completed_at,
            'tasks': [
                {
                    'title': task.title,
                    'status': task.status,
                    'assigned_agent': task.assigned_agent,
                    'estimated_cost': task.estimated_cost,
                    'stage': task.stage.value
                }
                for task in project.tasks
            ]
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