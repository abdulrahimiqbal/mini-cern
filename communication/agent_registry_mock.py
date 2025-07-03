"""
Mock Agent Registry - Testing Implementation Without Redis
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum

from agents.agent_types import AgentType, AgentCapability

logger = logging.getLogger(__name__)

class RegistrationStatus(Enum):
    """Agent registration status"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class RegistryEntry:
    """Registry entry for an agent"""
    agent_id: str
    agent_type: AgentType
    capabilities: List[AgentCapability]
    status: RegistrationStatus
    endpoint: str  # For communication
    load_factor: float = 0.0  # Current workload (0.0 = idle, 1.0 = fully loaded)
    reputation_score: float = 100.0
    last_heartbeat: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['agent_type'] = self.agent_type.value
        data['capabilities'] = [cap.value for cap in self.capabilities]
        data['status'] = self.status.value
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegistryEntry':
        """Create from dictionary"""
        data['agent_type'] = AgentType(data['agent_type'])
        data['capabilities'] = [AgentCapability(cap) for cap in data['capabilities']]
        data['status'] = RegistrationStatus(data['status'])
        data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        return cls(**data)

class AgentRegistry:
    """Mock agent registry for testing"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.agents: Dict[str, RegistryEntry] = {}  # Store agents in memory
        self.is_running = False
    
    async def initialize(self) -> None:
        """Initialize the mock agent registry"""
        self.is_running = True
        
        # Add some mock agents for testing
        await self._add_default_agents()
        
        logger.info("Mock agent registry initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the mock agent registry"""
        self.is_running = False
        logger.info("Mock agent registry shutdown")
    
    async def register_agent(self, entry: RegistryEntry) -> bool:
        """Register an agent in the registry"""
        try:
            entry.last_heartbeat = datetime.utcnow()
            self.agents[entry.agent_id] = entry
            logger.info(f"Registered agent {entry.agent_id} ({entry.agent_type.value})")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {entry.agent_id}: {e}")
            return False
    
    async def get_agent(self, agent_id: str) -> Optional[RegistryEntry]:
        """Get agent information by ID"""
        return self.agents.get(agent_id)
    
    async def find_best_agent_for_task(self, required_capabilities: List[AgentCapability], exclude_agents: Set[str] = None) -> Optional[RegistryEntry]:
        """Find the best available agent for a task"""
        if exclude_agents is None:
            exclude_agents = set()
        
        candidates = []
        for agent_id, agent in self.agents.items():
            if agent_id in exclude_agents:
                continue
            if agent.status not in [RegistrationStatus.ACTIVE, RegistrationStatus.IDLE]:
                continue
            
            agent_caps = set(agent.capabilities)
            required_caps = set(required_capabilities)
            
            if required_caps.issubset(agent_caps):
                candidates.append(agent)
        
        if not candidates:
            return None
        
        # Score based on load and reputation
        def score(agent):
            return (agent.reputation_score / 100.0) - agent.load_factor
        
        return max(candidates, key=score)
    
    async def get_all_agents(self) -> List[RegistryEntry]:
        """Get all registered agents"""
        return list(self.agents.values())
    
    async def find_agents_by_type(self, agent_type: AgentType) -> List[RegistryEntry]:
        """Find all agents of a specific type"""
        return [agent for agent in self.agents.values() if agent.agent_type == agent_type]
    
    async def find_agents_by_capability(self, capability: AgentCapability) -> List[RegistryEntry]:
        """Find all agents with a specific capability"""
        return [agent for agent in self.agents.values() if capability in agent.capabilities]
    
    async def get_agents_by_type(self, agent_type: AgentType) -> List[RegistryEntry]:
        """Get agents by type (alias for find_agents_by_type)"""
        return await self.find_agents_by_type(agent_type)
    
    async def update_agent_status(self, agent_id: str, status: RegistrationStatus, load_factor: float = None) -> bool:
        """Update an agent's status and load factor"""
        try:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            agent.status = status
            agent.last_heartbeat = datetime.utcnow()
            
            if load_factor is not None:
                agent.load_factor = load_factor
            
            return True
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id} status: {e}")
            return False
    
    async def heartbeat(self, agent_id: str) -> bool:
        """Record heartbeat for an agent"""
        return await self.update_agent_status(agent_id, RegistrationStatus.ACTIVE)
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        total_agents = len(self.agents)
        active_agents = sum(1 for agent in self.agents.values() if agent.status == RegistrationStatus.ACTIVE)
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "agents_by_type": {
                agent_type.value: len(await self.find_agents_by_type(agent_type))
                for agent_type in AgentType
                         },
             "average_load": sum(agent.load_factor for agent in self.agents.values()) / max(total_agents, 1),
             "timestamp": datetime.utcnow().isoformat()
         }
    
    async def _add_default_agents(self):
        """Add default mock agents for testing"""
        from agents.agent_types import AGENT_DEFAULT_CAPABILITIES
        
        # Create mock agents for each type
        agent_configs = [
            ("theory_agent_01", AgentType.THEORY, "http://localhost:8001"),
            ("experimental_agent_01", AgentType.EXPERIMENTAL, "http://localhost:8002"),
            ("analysis_agent_01", AgentType.ANALYSIS, "http://localhost:8003"),
            ("literature_agent_01", AgentType.LITERATURE, "http://localhost:8004"),
            ("safety_agent_01", AgentType.SAFETY, "http://localhost:8005"),
            ("meta_agent_01", AgentType.META, "http://localhost:8006"),
        ]
        
        for agent_id, agent_type, endpoint in agent_configs:
            # Get default capabilities and add some extra ones
            capabilities = AGENT_DEFAULT_CAPABILITIES.get(agent_type, []).copy()
            
            # Add extra capabilities for comprehensive testing
            if agent_type == AgentType.THEORY:
                capabilities.extend([AgentCapability.KNOWLEDGE_SYNTHESIS, AgentCapability.THEORY_VALIDATION])
            elif agent_type == AgentType.EXPERIMENTAL:
                capabilities.extend([AgentCapability.PROTOCOL_DEVELOPMENT, AgentCapability.INSTRUMENT_CONTROL])
            elif agent_type == AgentType.ANALYSIS:
                capabilities.extend([AgentCapability.STATISTICAL_ANALYSIS, AgentCapability.QUALITY_ASSESSMENT])
            elif agent_type == AgentType.LITERATURE:
                capabilities.extend([AgentCapability.KNOWLEDGE_SYNTHESIS])
            elif agent_type == AgentType.META:
                capabilities.extend([AgentCapability.REPORT_GENERATION, AgentCapability.SCIENTIFIC_WRITING])
            
            # Remove duplicates
            capabilities = list(set(capabilities))
            
            entry = RegistryEntry(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities=capabilities,
                status=RegistrationStatus.ACTIVE,
                endpoint=endpoint,
                load_factor=0.0,
                reputation_score=100.0
            )
            
            await self.register_agent(entry) 