"""
Science Research Institute - LLM Integration Layer
Unified interface for multiple LLM providers with research-specific optimizations
"""

from .llm_interface import LLMProvider, LLMResponse, ModelInfo
from .llm_manager import LLMManager
from .prompt_templates import RESEARCH_PROMPTS

__all__ = [
    'LLMProvider',
    'LLMResponse', 
    'ModelInfo',
    'LLMManager',
    'RESEARCH_PROMPTS'
] 