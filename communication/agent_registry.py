"""
Agent Registry - Dynamic Service Discovery and Capability Matching
Manages available agents and their capabilities for task assignment
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis

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
        """Convert to dictionary for Redis storage"""
        data = asdict(self)
        data['agent_type'] = self.agent_type.value
        data['capabilities'] = [cap.value for cap in self.capabilities]
        data['status'] = self.status.value
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegistryEntry':
        """Create from dictionary loaded from Redis"""
        data['agent_type'] = AgentType(data['agent_type'])
        data['capabilities'] = [AgentCapability(cap) for cap in data['capabilities']]
        data['status'] = RegistrationStatus(data['status'])
        data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        return cls(**data)

class AgentRegistry:
    """Central registry for agent service discovery"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.registry_key = "agent_registry"
        self.heartbeat_timeout = 60  # seconds
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def initialize(self) -> None:
        """Initialize the agent registry"""
        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            
            # Start cleanup task for stale entries
            self.cleanup_task = asyncio.create_task(self._cleanup_stale_entries())
            self.is_running = True
            
            logger.info("Agent registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent registry: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the agent registry"""
        self.is_running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.redis:
            await self.redis.close()
        
        logger.info("Agent registry shutdown complete")
    
    async def register_agent(self, entry: RegistryEntry) -> bool:
        """Register an agent in the registry"""
        try:
            entry.last_heartbeat = datetime.utcnow()
            entry_data = entry.to_dict()
            
            await self.redis.hset(self.registry_key, entry.agent_id, json.dumps(entry_data))
            
            logger.info(f"Registered agent {entry.agent_id} ({entry.agent_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {entry.agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry"""
        try:
            await self.redis.hdel(self.registry_key, agent_id)
            logger.info(f"Unregistered agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    async def update_agent_status(self, agent_id: str, status: RegistrationStatus, load_factor: float = None) -> bool:
        """Update an agent's status and load factor"""
        try:
            entry_data = await self.redis.hget(self.registry_key, agent_id)
            if not entry_data:
                logger.warning(f"Agent {agent_id} not found in registry")
                return False
            
            entry = RegistryEntry.from_dict(json.loads(entry_data))
            entry.status = status
            entry.last_heartbeat = datetime.utcnow()
            
            if load_factor is not None:
                entry.load_factor = load_factor
            
            await self.redis.hset(self.registry_key, agent_id, json.dumps(entry.to_dict()))
            
            logger.debug(f"Updated agent {agent_id} status to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id} status: {e}")
            return False
    
    async def heartbeat(self, agent_id: str) -> bool:
        """Record heartbeat for an agent"""
        return await self.update_agent_status(agent_id, RegistrationStatus.ACTIVE)
    
    async def get_agent(self, agent_id: str) -> Optional[RegistryEntry]:
        """Get agent information by ID"""
        try:
            entry_data = await self.redis.hget(self.registry_key, agent_id)
            if not entry_data:
                return None
            
            return RegistryEntry.from_dict(json.loads(entry_data))
            
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            return None
    
    async def get_all_agents(self) -> List[RegistryEntry]:
        """Get all registered agents"""
        try:
            all_entries = await self.redis.hgetall(self.registry_key)
            agents = []
            
            for agent_id, entry_data in all_entries.items():
                try:
                    entry = RegistryEntry.from_dict(json.loads(entry_data))
                    agents.append(entry)
                except Exception as e:
                    logger.warning(f"Failed to parse entry for agent {agent_id}: {e}")
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to get all agents: {e}")
            return []
    
    async def find_agents_by_type(self, agent_type: AgentType) -> List[RegistryEntry]:
        """Find all agents of a specific type"""
        all_agents = await self.get_all_agents()
        return [agent for agent in all_agents if agent.agent_type == agent_type]
    
    async def find_agents_by_capability(self, capability: AgentCapability) -> List[RegistryEntry]:
        """Find all agents with a specific capability"""
        all_agents = await self.get_all_agents()
        return [agent for agent in all_agents if capability in agent.capabilities]
    
    async def find_best_agent_for_task(self, required_capabilities: List[AgentCapability], exclude_agents: Set[str] = None) -> Optional[RegistryEntry]:
        """Find the best available agent for a task"""
        if exclude_agents is None:
            exclude_agents = set()
        
        # Get all agents with required capabilities
        candidate_agents = []
        all_agents = await self.get_all_agents()
        
        for agent in all_agents:
            if agent.agent_id in exclude_agents:
                continue
            
            if agent.status not in [RegistrationStatus.ACTIVE, RegistrationStatus.IDLE]:
                continue
            
            # Check if agent has all required capabilities
            agent_caps = set(agent.capabilities)
            required_caps = set(required_capabilities)
            
            if required_caps.issubset(agent_caps):
                candidate_agents.append(agent)
        
        if not candidate_agents:
            return None
        
        # Score agents based on load factor and reputation
        def agent_score(agent: RegistryEntry) -> float:
            # Lower load factor is better, higher reputation is better
            load_penalty = agent.load_factor  # 0.0 to 1.0
            reputation_bonus = agent.reputation_score / 100.0  # 0.0 to 1.0+
            return reputation_bonus - load_penalty
        
        # Return agent with highest score
        best_agent = max(candidate_agents, key=agent_score)
        return best_agent
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        all_agents = await self.get_all_agents()
        
        metrics = {
            "total_agents": len(all_agents),
            "agents_by_status": {},
            "agents_by_type": {},
            "average_load": 0.0,
            "average_reputation": 0.0
        }
        
        if not all_agents:
            return metrics
        
        # Calculate status distribution
        for agent in all_agents:
            status = agent.status.value
            metrics["agents_by_status"][status] = metrics["agents_by_status"].get(status, 0) + 1
            
            agent_type = agent.agent_type.value
            metrics["agents_by_type"][agent_type] = metrics["agents_by_type"].get(agent_type, 0) + 1
        
        # Calculate averages
        total_load = sum(agent.load_factor for agent in all_agents)
        total_reputation = sum(agent.reputation_score for agent in all_agents)
        
        metrics["average_load"] = total_load / len(all_agents)
        metrics["average_reputation"] = total_reputation / len(all_agents)
        
        return metrics
    
    async def _cleanup_stale_entries(self) -> None:
        """Remove stale agent entries (background task)"""
        while self.is_running:
            try:
                cutoff_time = datetime.utcnow() - timedelta(seconds=self.heartbeat_timeout)
                all_agents = await self.get_all_agents()
                
                stale_agents = [
                    agent.agent_id for agent in all_agents
                    if agent.last_heartbeat < cutoff_time
                ]
                
                for agent_id in stale_agents:
                    await self.update_agent_status(agent_id, RegistrationStatus.OFFLINE)
                    logger.info(f"Marked agent {agent_id} as offline due to stale heartbeat")
                
                # Clean up after 10 minutes offline
                cleanup_cutoff = datetime.utcnow() - timedelta(minutes=10)
                for agent in all_agents:
                    if (agent.status == RegistrationStatus.OFFLINE and 
                        agent.last_heartbeat < cleanup_cutoff):
                        await self.unregister_agent(agent.agent_id)
                        logger.info(f"Removed stale agent {agent.agent_id} from registry")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(30)
    
    async def get_agent_load_balancing_info(self) -> Dict[str, Any]:
        """Get load balancing information for the system"""
        all_agents = await self.get_all_agents()
        active_agents = [a for a in all_agents if a.status in [RegistrationStatus.ACTIVE, RegistrationStatus.IDLE]]
        
        load_info = {
            "total_capacity": len(active_agents),
            "current_load": sum(a.load_factor for a in active_agents),
            "available_capacity": sum(1.0 - a.load_factor for a in active_agents),
            "agents_by_load": {
                "idle": len([a for a in active_agents if a.load_factor < 0.1]),
                "light": len([a for a in active_agents if 0.1 <= a.load_factor < 0.5]),
                "moderate": len([a for a in active_agents if 0.5 <= a.load_factor < 0.8]),
                "heavy": len([a for a in active_agents if a.load_factor >= 0.8])
            }
        }
        
        return load_info 