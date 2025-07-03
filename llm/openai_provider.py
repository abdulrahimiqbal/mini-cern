"""
OpenAI Provider
Implementation of LLM interface for OpenAI GPT models
"""

import time
import logging
from typing import List, Dict, Any, Optional
import openai
from openai import AsyncOpenAI

from .llm_interface import LLMProvider, LLMResponse, LLMMessage, ModelInfo, ModelCapability

logger = logging.getLogger(__name__)

class LLMIntegrationError(Exception):
    """Error in LLM integration"""
    pass

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider for research tasks"""
    
    def __init__(self, api_key: str):
        super().__init__("openai")
        self.api_key = api_key
        self.client: Optional[AsyncOpenAI] = None
        
        # OpenAI model configurations
        self.models = {
            "gpt-4-turbo": ModelInfo(
                name="gpt-4-turbo",
                provider="openai",
                max_tokens=4096,
                input_cost_per_token=0.00001,  # $0.01 per 1K tokens
                output_cost_per_token=0.00003,  # $0.03 per 1K tokens
                capabilities=[
                    ModelCapability.MATHEMATICAL_REASONING,
                    ModelCapability.SCIENTIFIC_ANALYSIS
                ],
                context_window=128000
            ),
            "gpt-3.5-turbo": ModelInfo(
                name="gpt-3.5-turbo",
                provider="openai",
                max_tokens=4096,
                input_cost_per_token=0.0000005,  # $0.0005 per 1K tokens
                output_cost_per_token=0.0000015,  # $0.0015 per 1K tokens
                capabilities=[
                    ModelCapability.TEXT_GENERATION
                ],
                context_window=16384
            )
        }
        
        self.default_model = "gpt-4-turbo"
    
    async def initialize(self) -> None:
        """Initialize OpenAI client"""
        try:
            self.client = AsyncOpenAI(api_key=self.api_key)
            
            # Test connection
            test_working = await self.test_connection()
            if not test_working:
                raise LLMIntegrationError("OpenAI connection test failed", provider="openai")
            
            self.is_initialized = True
            logger.info("OpenAI provider initialized successfully")
            
        except Exception as e:
            raise LLMIntegrationError(f"Failed to initialize OpenAI: {e}", provider="openai")
    
    async def generate(
        self, 
        prompt: str, 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text from a prompt"""
        if not self.is_initialized:
            raise LLMIntegrationError("Provider not initialized", provider="openai")
        
        model = model or self.default_model
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_time = time.time() - start_time
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            # Calculate cost
            model_info = self.get_model_info(model)
            cost = 0.0
            if model_info and usage:
                cost = (
                    usage.prompt_tokens * model_info.input_cost_per_token +
                    usage.completion_tokens * model_info.output_cost_per_token
                )
            
            llm_response = LLMResponse(
                content=content,
                success=True,
                model_used=model,
                provider=self.provider_name,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
                cost_usd=cost,
                response_time_seconds=response_time
            )
            
            self.update_usage_stats(llm_response)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            error_response = LLMResponse(
                content="",
                success=False,
                model_used=model,
                provider=self.provider_name,
                error_message=str(e),
                response_time_seconds=response_time
            )
            
            self.update_usage_stats(error_response)
            logger.error(f"OpenAI generation failed: {e}")
            return error_response
    
    async def chat(
        self, 
        messages: List[LLMMessage], 
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Have a conversation with the model"""
        if not self.is_initialized:
            raise LLMIntegrationError("Provider not initialized", provider="openai")
        
        model = model or self.default_model
        start_time = time.time()
        
        try:
            # Convert LLMMessage to OpenAI format
            openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_time = time.time() - start_time
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            # Calculate cost
            model_info = self.get_model_info(model)
            cost = 0.0
            if model_info and usage:
                cost = (
                    usage.prompt_tokens * model_info.input_cost_per_token +
                    usage.completion_tokens * model_info.output_cost_per_token
                )
            
            llm_response = LLMResponse(
                content=content,
                success=True,
                model_used=model,
                provider=self.provider_name,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
                cost_usd=cost,
                response_time_seconds=response_time
            )
            
            self.update_usage_stats(llm_response)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            error_response = LLMResponse(
                content="",
                success=False,
                model_used=model,
                provider=self.provider_name,
                error_message=str(e),
                response_time_seconds=response_time
            )
            
            self.update_usage_stats(error_response)
            logger.error(f"OpenAI chat failed: {e}")
            return error_response
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available OpenAI models"""
        return list(self.models.values())
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        return self.models.get(model_name)
    
    def get_best_model_for_task(self, task_type: str) -> str:
        """Get the best OpenAI model for a specific task"""
        if task_type in ["mathematical_reasoning", "scientific_analysis", "complex_research"]:
            return "gpt-4-turbo"
        elif task_type in ["code_generation", "data_analysis"]:
            return "gpt-4-turbo"
        else:
            return "gpt-3.5-turbo"  # For simpler tasks 