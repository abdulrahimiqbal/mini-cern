"""Mock Agent Implementations for Testing"""

import asyncio
import random
from typing import Dict, Any

from .base_agent import BaseAgent, AgentTask
from .agent_types import AgentType, AgentCapabilities, VirtualsAgentConfig, AGENT_DEFAULT_CAPABILITIES

class MockTheoryAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        agent_id = agent_id or f"theory_{random.randint(1000, 9999)}"
        
        capabilities = AgentCapabilities(
            agent_type=AgentType.THEORY,
            capabilities=AGENT_DEFAULT_CAPABILITIES[AgentType.THEORY],
            research_domains=["quantum_mechanics", "optics"],
            specialization_level=7.5
        )
        
        virtuals_config = VirtualsAgentConfig(revenue_sharing_enabled=True, token_rewards_per_task=5.0)
        super().__init__(agent_id, AgentType.THEORY, capabilities, virtuals_config)
    
    async def _agent_initialize(self) -> None:
        await asyncio.sleep(0.1)
    
    async def _execute_task_implementation(self, task: AgentTask) -> Dict[str, Any]:
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        return {
            "task_type": task.task_type.value,
            "result": f"Theory analysis for: {task.title}",
            "hypotheses": [
                "Quantum interference effects dominate",
                "Classical approximation breaks down"
            ],
            "confidence": random.uniform(0.8, 0.95),
            "mathematical_model": "H = H₀ + V(r,t)"
        }

class MockExperimentalAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        agent_id = agent_id or f"experimental_{random.randint(1000, 9999)}"
        
        capabilities = AgentCapabilities(
            agent_type=AgentType.EXPERIMENTAL,
            capabilities=AGENT_DEFAULT_CAPABILITIES[AgentType.EXPERIMENTAL],
            research_domains=["optics", "instrumentation"],
            specialization_level=8.0
        )
        
        virtuals_config = VirtualsAgentConfig(revenue_sharing_enabled=True, token_rewards_per_task=7.0)
        super().__init__(agent_id, AgentType.EXPERIMENTAL, capabilities, virtuals_config)
    
    async def _agent_initialize(self) -> None:
        await asyncio.sleep(0.1)
    
    async def _execute_task_implementation(self, task: AgentTask) -> Dict[str, Any]:
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        return {
            "task_type": task.task_type.value,
            "result": f"Experimental design for: {task.title}",
            "setup": "Optical measurement system",
            "equipment": ["laser", "detector", "sample_holder"],
            "expected_precision": f"±{random.uniform(0.1, 5.0):.2f}%",
            "duration_estimate": f"{random.uniform(2, 24):.1f} hours",
            "confidence": random.uniform(0.82, 0.96)
        }

class MockAnalysisAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        agent_id = agent_id or f"analysis_{random.randint(1000, 9999)}"
        
        capabilities = AgentCapabilities(
            agent_type=AgentType.ANALYSIS,
            capabilities=AGENT_DEFAULT_CAPABILITIES[AgentType.ANALYSIS],
            research_domains=["data_analysis", "statistics"],
            specialization_level=8.5
        )
        
        virtuals_config = VirtualsAgentConfig(revenue_sharing_enabled=True, token_rewards_per_task=6.0)
        super().__init__(agent_id, AgentType.ANALYSIS, capabilities, virtuals_config)
    
    async def _agent_initialize(self) -> None:
        await asyncio.sleep(0.1)
    
    async def _execute_task_implementation(self, task: AgentTask) -> Dict[str, Any]:
        await asyncio.sleep(random.uniform(0.8, 2.5))
        
        return {
            "task_type": task.task_type.value,
            "result": f"Data analysis for: {task.title}",
            "statistics": {
                "mean": f"{random.uniform(50, 150):.3f}",
                "std_dev": f"{random.uniform(5, 20):.3f}",
                "p_value": random.uniform(0.001, 0.1)
            },
            "trends": "Statistically significant results",
            "recommendations": ["Increase sample size", "Validate results"],
            "confidence": random.uniform(0.88, 0.97)
        } 