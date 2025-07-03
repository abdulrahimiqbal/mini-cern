"""
LLM Interface
Abstract interface for all LLM providers with research-specific functionality
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ModelCapability(Enum):
    """Capabilities that LLM models can have"""
    TEXT_GENERATION = "text_generation"
    MATHEMATICAL_REASONING = "mathematical_reasoning"
    CODE_GENERATION = "code_generation"
    SCIENTIFIC_ANALYSIS = "scientific_analysis"
    FUNCTION_CALLING = "function_calling"
    MULTIMODAL = "multimodal"
    LONG_CONTEXT = "long_context"

@dataclass
class ModelInfo:
    """Information about an LLM model"""
    name: str
    provider: str
    max_tokens: int
    input_cost_per_token: float  # USD
    output_cost_per_token: float  # USD
    capabilities: List[ModelCapability]
    context_window: int
    training_cutoff: Optional[str] = None
    
    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports a specific capability"""
        return capability in self.capabilities

@dataclass
class LLMMessage:
    """Single message in a conversation"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class LLMResponse:
    """Response from an LLM provider"""
    content: str
    success: bool
    model_used: str
    provider: str
    
    # Usage statistics
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    
    # Quality metrics
    confidence_score: Optional[float] = None
    reasoning_steps: Optional[List[str]] = None
    
    # Error information
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Timing
    response_time_seconds: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens

class LLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.is_initialized = False
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider"""
        pass
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text from a prompt"""
        pass
    
    @abstractmethod
    async def chat(
        self, 
        messages: List[LLMMessage], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Have a conversation with the model"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        pass
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get provider usage statistics"""
        return self.usage_stats.copy()
    
    def update_usage_stats(self, response: LLMResponse) -> None:
        """Update usage statistics"""
        self.usage_stats["total_requests"] += 1
        if response.success:
            self.usage_stats["successful_requests"] += 1
        self.usage_stats["total_tokens"] += response.total_tokens
        self.usage_stats["total_cost"] += response.cost_usd
    
    async def test_connection(self) -> bool:
        """Test if the provider is working"""
        try:
            test_response = await self.generate("Hello", max_tokens=10)
            return test_response.success
        except Exception:
            return False 