"""
LLM Manager
Coordinates multiple LLM providers with intelligent routing and fallback
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from enum import Enum

from .llm_interface import LLMProvider, LLMResponse, LLMMessage, ModelCapability
from .openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

class LLMIntegrationError(Exception):
    """Error in LLM integration"""
    pass

class TaskComplexity(Enum):
    """Complexity levels for LLM task routing"""
    SIMPLE = "simple"
    MODERATE = "moderate" 
    COMPLEX = "complex"
    EXPERT = "expert"

class LLMManager:
    """
    Manages multiple LLM providers with intelligent routing and fallback
    Integrates with Virtuals Protocol for agent economics
    """
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.is_initialized = False
        
        # Provider priority (higher = preferred)
        self.provider_priority = {
            "openai": 100,
            "anthropic": 90
        }
        
        # Task routing rules
        self.task_routing = {
            "mathematical_reasoning": ("openai", "gpt-4-turbo"),
            "scientific_analysis": ("openai", "gpt-4-turbo"),
            "hypothesis_generation": ("openai", "gpt-4-turbo"),
            "experimental_design": ("openai", "gpt-4-turbo"),
            "data_analysis": ("openai", "gpt-4-turbo"),
            "literature_review": ("openai", "gpt-3.5-turbo"),
            "simple_text": ("openai", "gpt-3.5-turbo")
        }
        
        # Usage tracking
        self.total_requests = 0
        self.total_cost = 0.0
        self.provider_usage = {}
    
    async def initialize(self, openai_api_key: str = None, anthropic_api_key: str = None) -> None:
        """Initialize all available providers"""
        try:
            # Initialize OpenAI if API key provided
            if openai_api_key:
                openai_provider = OpenAIProvider(openai_api_key)
                await openai_provider.initialize()
                self.providers["openai"] = openai_provider
                self.provider_usage["openai"] = {"requests": 0, "cost": 0.0}
                logger.info("OpenAI provider initialized")
            
            # Initialize Anthropic if API key provided
            if anthropic_api_key:
                # We'll add this in a future iteration
                logger.info("Anthropic provider not yet implemented")
            
            if not self.providers:
                raise LLMIntegrationError("No LLM providers available")
            
            self.is_initialized = True
            logger.info(f"LLM Manager initialized with {len(self.providers)} providers")
            
        except Exception as e:
            raise LLMIntegrationError(f"Failed to initialize LLM Manager: {e}")
    
    async def generate_for_agent(
        self,
        prompt: str,
        agent_type: str,
        task_type: str = "general",
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate text optimized for specific agent type and task"""
        if not self.is_initialized:
            raise LLMIntegrationError("LLM Manager not initialized")
        
        # Get optimal provider and model
        provider_name, model = self._get_optimal_provider_and_model(task_type, complexity)
        
        try:
            provider = self.providers[provider_name]
            response = await provider.generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Track usage
            self._update_usage_stats(provider_name, response)
            
            logger.info(f"Generated response for {agent_type} using {provider_name}/{model}")
            return response
            
        except Exception as e:
            # Try fallback provider
            fallback_response = await self._try_fallback(prompt, provider_name, max_tokens, temperature)
            if fallback_response:
                return fallback_response
            
            # If all providers fail, return error response
            return LLMResponse(
                content="",
                success=False,
                model_used="unknown",
                provider="unknown",
                error_message=f"All providers failed: {e}"
            )
    
    async def chat_for_agent(
        self,
        messages: List[LLMMessage],
        agent_type: str,
        task_type: str = "general",
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Chat conversation optimized for specific agent type"""
        if not self.is_initialized:
            raise LLMIntegrationError("LLM Manager not initialized")
        
        # Get optimal provider and model
        provider_name, model = self._get_optimal_provider_and_model(task_type, complexity)
        
        try:
            provider = self.providers[provider_name]
            response = await provider.chat(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Track usage
            self._update_usage_stats(provider_name, response)
            
            logger.info(f"Chat response for {agent_type} using {provider_name}/{model}")
            return response
            
        except Exception as e:
            # Try fallback
            fallback_response = await self._try_chat_fallback(messages, provider_name, max_tokens, temperature)
            if fallback_response:
                return fallback_response
            
            return LLMResponse(
                content="",
                success=False,
                model_used="unknown",
                provider="unknown", 
                error_message=f"All providers failed: {e}"
            )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        return {
            "total_requests": self.total_requests,
            "total_cost": self.total_cost,
            "provider_usage": self.provider_usage.copy(),
            "available_providers": list(self.providers.keys()),
            "is_initialized": self.is_initialized
        }
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get all available models by provider"""
        models = {}
        for provider_name, provider in self.providers.items():
            model_infos = provider.get_available_models()
            models[provider_name] = [model.name for model in model_infos]
        return models
    
    async def test_all_providers(self) -> Dict[str, bool]:
        """Test connectivity to all providers"""
        results = {}
        for provider_name, provider in self.providers.items():
            try:
                results[provider_name] = await provider.test_connection()
            except Exception as e:
                logger.error(f"Provider {provider_name} test failed: {e}")
                results[provider_name] = False
        return results
    
    # Private helper methods
    def _get_optimal_provider_and_model(self, task_type: str, complexity: TaskComplexity) -> tuple[str, str]:
        """Get the best provider and model for a task"""
        
        # Check if we have a specific routing rule
        if task_type in self.task_routing:
            provider_name, model = self.task_routing[task_type]
            if provider_name in self.providers:
                return provider_name, model
        
        # Fallback to best available provider
        best_provider = self._get_best_available_provider()
        
        # Select model based on complexity
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXPERT]:
            model = "gpt-4-turbo"
        else:
            model = "gpt-3.5-turbo"
        
        return best_provider, model
    
    def _get_best_available_provider(self) -> str:
        """Get the highest priority available provider"""
        available_providers = [
            (name, self.provider_priority.get(name, 0))
            for name in self.providers.keys()
        ]
        
        if not available_providers:
            raise LLMIntegrationError("No providers available")
        
        # Sort by priority (highest first)
        available_providers.sort(key=lambda x: x[1], reverse=True)
        return available_providers[0][0]
    
    async def _try_fallback(self, prompt: str, failed_provider: str, max_tokens: int, temperature: float) -> Optional[LLMResponse]:
        """Try fallback providers if primary fails"""
        for provider_name, provider in self.providers.items():
            if provider_name != failed_provider:
                try:
                    logger.info(f"Trying fallback provider: {provider_name}")
                    response = await provider.generate(prompt, max_tokens=max_tokens, temperature=temperature)
                    self._update_usage_stats(provider_name, response)
                    return response
                except Exception as e:
                    logger.warning(f"Fallback provider {provider_name} also failed: {e}")
                    continue
        return None
    
    async def _try_chat_fallback(self, messages: List[LLMMessage], failed_provider: str, max_tokens: int, temperature: float) -> Optional[LLMResponse]:
        """Try fallback providers for chat if primary fails"""
        for provider_name, provider in self.providers.items():
            if provider_name != failed_provider:
                try:
                    logger.info(f"Trying chat fallback provider: {provider_name}")
                    response = await provider.chat(messages, max_tokens=max_tokens, temperature=temperature)
                    self._update_usage_stats(provider_name, response)
                    return response
                except Exception as e:
                    logger.warning(f"Chat fallback provider {provider_name} also failed: {e}")
                    continue
        return None
    
    def _update_usage_stats(self, provider_name: str, response: LLMResponse) -> None:
        """Update usage statistics"""
        self.total_requests += 1
        self.total_cost += response.cost_usd
        
        if provider_name in self.provider_usage:
            self.provider_usage[provider_name]["requests"] += 1
            self.provider_usage[provider_name]["cost"] += response.cost_usd 