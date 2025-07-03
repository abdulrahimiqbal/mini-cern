"""
Agent Type Definitions and Enums
Defines the different types of research agents and their capabilities
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentType(Enum):
    """Types of research agents in the system"""
    THEORY = "theory"
    EXPERIMENTAL = "experimental"
    ANALYSIS = "analysis"
    LITERATURE = "literature"
    SAFETY = "safety"
    META = "meta"

class AgentCapability(Enum):
    """Specific capabilities that agents can have"""
    MATHEMATICAL_MODELING = "mathematical_modeling"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EXPERIMENTAL_DESIGN = "experimental_design"
    DATA_ANALYSIS = "data_analysis"
    DATA_COLLECTION = "data_collection"
    LITERATURE_SEARCH = "literature_search"
    SAFETY_ASSESSMENT = "safety_assessment"
    PROTOCOL_OPTIMIZATION = "protocol_optimization"
    RESULT_INTERPRETATION = "result_interpretation"
    PEER_REVIEW = "peer_review"
    COLLABORATION = "collaboration"
    
    # Additional capabilities for workflow engine
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    PROTOCOL_DEVELOPMENT = "protocol_development"
    RISK_ANALYSIS = "risk_analysis"
    INSTRUMENT_CONTROL = "instrument_control"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    THEORY_VALIDATION = "theory_validation"
    QUALITY_ASSESSMENT = "quality_assessment"
    REPORT_GENERATION = "report_generation"
    SCIENTIFIC_WRITING = "scientific_writing"

class ResearchRole(Enum):
    """Roles agents can play in research projects"""
    PRIMARY_INVESTIGATOR = "primary_investigator"
    COLLABORATOR = "collaborator"
    REVIEWER = "reviewer"
    CONSULTANT = "consultant"
    MONITOR = "monitor"

class AgentState(Enum):
    """Current state of an agent"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    OFFLINE = "offline"

class TaskType(Enum):
    """Types of tasks agents can execute"""
    RESEARCH_PLANNING = "research_planning"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EXPERIMENTAL_DESIGN = "experimental_design"
    DATA_COLLECTION = "data_collection"
    DATA_ANALYSIS = "data_analysis"
    LITERATURE_REVIEW = "literature_review"
    RESULT_SYNTHESIS = "result_synthesis"
    SAFETY_CHECK = "safety_check"
    PEER_REVIEW = "peer_review"
    COLLABORATION = "collaboration"

class TaskPriority(Enum):
    """Priority levels for agent tasks"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class VirtualsAgentConfig:
    """Configuration for Virtuals Protocol integration"""
    agent_token_symbol: Optional[str] = None  # e.g., "THEORY-001"
    performance_metrics_endpoint: Optional[str] = None
    revenue_sharing_enabled: bool = False
    token_rewards_per_task: float = 0.0
    stake_required: float = 0.0
    reputation_score: float = 100.0  # Starting reputation
    
    # Virtuals GAME framework integration
    game_participation: bool = False
    collaborative_rewards: bool = True
    competitive_challenges: bool = False

@dataclass
class AgentCapabilities:
    """Detailed capability specification for an agent"""
    agent_type: AgentType
    capabilities: List[AgentCapability]
    research_domains: List[str]  # e.g., ["quantum", "optics", "mechanics"]
    max_concurrent_tasks: int = 1
    specialization_level: float = 1.0  # 0.0 to 10.0
    collaboration_preference: float = 5.0  # 0.0 (solo) to 10.0 (team-oriented)
    
    # Performance characteristics
    avg_task_completion_time: float = 3600.0  # seconds
    success_rate: float = 0.95
    cost_per_hour: float = 50.0  # USD
    
    # Virtuals integration
    virtuals_config: VirtualsAgentConfig = None
    
    def __post_init__(self):
        if self.virtuals_config is None:
            self.virtuals_config = VirtualsAgentConfig()

@dataclass
class AgentMetrics:
    """Performance and economic metrics for an agent"""
    # Performance metrics
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_runtime_hours: float = 0.0
    average_task_time: float = 0.0
    success_rate: float = 1.0
    
    # Economic metrics (Virtuals Protocol)
    tokens_earned: float = 0.0
    tokens_staked: float = 0.0
    revenue_generated: float = 0.0
    cost_incurred: float = 0.0
    
    # Collaboration metrics
    collaborations_initiated: int = 0
    collaborations_joined: int = 0
    peer_reviews_completed: int = 0
    citations_received: int = 0
    
    # Quality metrics
    reputation_score: float = 100.0
    research_impact_score: float = 0.0
    innovation_index: float = 0.0
    
    # Timestamps
    created_at: datetime = None
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()
    
    def update_success_rate(self):
        """Recalculate success rate based on completed/failed tasks"""
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks > 0:
            self.success_rate = self.tasks_completed / total_tasks
        self.last_updated = datetime.utcnow()
    
    def calculate_efficiency_score(self) -> float:
        """Calculate overall efficiency score for Virtuals Protocol ranking"""
        if self.total_runtime_hours == 0:
            return 0.0
        
        # Weighted efficiency score
        time_efficiency = 1.0 / max(self.average_task_time / 3600.0, 0.1)  # Hours
        quality_score = self.success_rate * (self.reputation_score / 100.0)
        collaboration_bonus = min(self.collaborations_initiated * 0.1, 1.0)
        
        return (time_efficiency * 0.4 + quality_score * 0.5 + collaboration_bonus * 0.1)

# Agent type to default capabilities mapping
AGENT_DEFAULT_CAPABILITIES = {
    AgentType.THEORY: [
        AgentCapability.MATHEMATICAL_MODELING,
        AgentCapability.HYPOTHESIS_GENERATION,
        AgentCapability.RESULT_INTERPRETATION,
        AgentCapability.COLLABORATION
    ],
    AgentType.EXPERIMENTAL: [
        AgentCapability.EXPERIMENTAL_DESIGN,
        AgentCapability.PROTOCOL_OPTIMIZATION,
        AgentCapability.DATA_COLLECTION,
        AgentCapability.SAFETY_ASSESSMENT
    ],
    AgentType.ANALYSIS: [
        AgentCapability.DATA_ANALYSIS,
        AgentCapability.RESULT_INTERPRETATION,
        AgentCapability.PEER_REVIEW,
        AgentCapability.COLLABORATION
    ],
    AgentType.LITERATURE: [
        AgentCapability.LITERATURE_SEARCH,
        AgentCapability.PEER_REVIEW,
        AgentCapability.RESULT_INTERPRETATION,
        AgentCapability.COLLABORATION
    ],
    AgentType.SAFETY: [
        AgentCapability.SAFETY_ASSESSMENT,
        AgentCapability.PROTOCOL_OPTIMIZATION,
        AgentCapability.PEER_REVIEW
    ],
    AgentType.META: [
        AgentCapability.COLLABORATION,
        AgentCapability.PEER_REVIEW,
        AgentCapability.PROTOCOL_OPTIMIZATION,
        AgentCapability.RESULT_INTERPRETATION
    ]
}

# Research domain specializations
PHYSICS_DOMAINS = [
    "quantum_mechanics",
    "optics",
    "solid_state",
    "atomic_physics",
    "particle_physics",
    "condensed_matter",
    "thermodynamics",
    "electromagnetism",
    "relativity",
    "cosmology",
    "biophysics",
    "medical_physics"
] 