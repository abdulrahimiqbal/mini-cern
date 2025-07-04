"""
Advanced LLM Manager for Phase 6 - Autonomous Research
Handles multi-model routing and specialized AI capabilities
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Import existing LLM infrastructure
import sys
sys.path.append('..')
from llm.llm_interface import LLMInterface
from llm.openai_provider import OpenAIProvider

class TaskType(Enum):
    """Types of research tasks that require different LLM specializations"""
    REASONING = "reasoning"
    CODING = "coding"
    MATHEMATICAL = "mathematical"
    EXPERIMENTAL = "experimental"
    LITERATURE = "literature"
    SAFETY = "safety"
    HYPOTHESIS = "hypothesis"
    ANALYSIS = "analysis"

@dataclass
class ResearchContext:
    """Context for research tasks"""
    domain: str
    topic: str
    previous_findings: List[str]
    constraints: Dict[str, Any]
    priority: str
    budget_remaining: float

@dataclass
class LLMResponse:
    """Standardized response from LLM operations"""
    content: str
    confidence: float
    reasoning: str
    sources: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime
    model_used: str
    cost: float

class AdvancedLLMManager:
    """
    Advanced LLM Manager for autonomous research
    Routes tasks to specialized models and manages context
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Model configuration for different task types
        self.model_config = {
            TaskType.REASONING: {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.1,
                'max_tokens': 4000,
                'description': 'Complex logical reasoning and problem solving'
            },
            TaskType.CODING: {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.2,
                'max_tokens': 3000,
                'description': 'Code generation and technical implementation'
            },
            TaskType.MATHEMATICAL: {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.1,
                'max_tokens': 2000,
                'description': 'Mathematical proofs and symbolic computation'
            },
            TaskType.EXPERIMENTAL: {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.3,
                'max_tokens': 3000,
                'description': 'Experimental design and methodology'
            },
            TaskType.LITERATURE: {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.4,
                'max_tokens': 4000,
                'description': 'Literature analysis and synthesis'
            },
            TaskType.SAFETY: {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.1,
                'max_tokens': 2000,
                'description': 'Safety validation and risk assessment'
            },
            TaskType.HYPOTHESIS: {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.5,
                'max_tokens': 2000,
                'description': 'Creative hypothesis generation'
            },
            TaskType.ANALYSIS: {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.2,
                'max_tokens': 3000,
                'description': 'Data analysis and interpretation'
            }
        }
        
        # Initialize LLM providers
        self.providers = {
            'openai': OpenAIProvider()
        }
        
        # Context management
        self.active_contexts = {}
        self.conversation_history = {}
        
    async def route_task(self, 
                        task_type: TaskType, 
                        prompt: str, 
                        context: Optional[ResearchContext] = None,
                        **kwargs) -> LLMResponse:
        """
        Route a task to the appropriate specialized model
        """
        try:
            config = self.model_config[task_type]
            
            # Build enhanced prompt with context
            enhanced_prompt = self._build_enhanced_prompt(
                prompt, task_type, context, **kwargs
            )
            
            # Get response from appropriate model
            response = await self._call_model(
                model=config['model'],
                prompt=enhanced_prompt,
                temperature=config['temperature'],
                max_tokens=config['max_tokens']
            )
            
            # Process and validate response
            processed_response = self._process_response(
                response, task_type, config
            )
            
            # Store in context if needed
            if context:
                self._update_context(context, processed_response)
            
            return processed_response
            
        except Exception as e:
            self.logger.error(f"Error routing task {task_type}: {str(e)}")
            raise
    
    def _build_enhanced_prompt(self, 
                              prompt: str, 
                              task_type: TaskType, 
                              context: Optional[ResearchContext],
                              **kwargs) -> str:
        """Build context-aware prompt for the specific task type"""
        
        base_prompts = {
            TaskType.REASONING: """You are an expert scientific reasoner. Analyze the given problem using rigorous logical reasoning. Provide step-by-step analysis and clear conclusions.""",
            
            TaskType.CODING: """You are an expert programmer specializing in scientific computing. Write clean, efficient, and well-documented code. Include error handling and testing considerations.""",
            
            TaskType.MATHEMATICAL: """You are a mathematical expert. Provide rigorous mathematical analysis, proofs, and derivations. Show all steps clearly and verify your work.""",
            
            TaskType.EXPERIMENTAL: """You are an experimental scientist. Design robust experiments with proper controls, statistical power, and methodological rigor. Consider potential confounds and limitations.""",
            
            TaskType.LITERATURE: """You are a research analyst. Synthesize information from multiple sources, identify key findings, gaps, and contradictions. Provide comprehensive and critical analysis.""",
            
            TaskType.SAFETY: """You are a safety expert. Evaluate potential risks, ethical implications, and safety measures. Provide comprehensive risk assessment and mitigation strategies.""",
            
            TaskType.HYPOTHESIS: """You are a creative scientific thinker. Generate novel, testable hypotheses based on available evidence. Think outside conventional frameworks while maintaining scientific rigor.""",
            
            TaskType.ANALYSIS: """You are a data analyst. Interpret results objectively, identify patterns and significance, and draw valid conclusions. Consider statistical validity and potential biases."""
        }
        
        enhanced_prompt = base_prompts[task_type] + "\n\n"
        
        # Add context if available
        if context:
            enhanced_prompt += f"""
Research Context:
- Domain: {context.domain}
- Topic: {context.topic}
- Previous findings: {', '.join(context.previous_findings) if context.previous_findings else 'None'}
- Constraints: {json.dumps(context.constraints, indent=2)}
- Priority: {context.priority}
- Budget remaining: ${context.budget_remaining:,.2f}

"""
        
        # Add the actual task
        enhanced_prompt += f"Task: {prompt}\n\n"
        
        # Add task-specific instructions
        if task_type == TaskType.REASONING:
            enhanced_prompt += "Please provide: 1) Clear logical analysis, 2) Step-by-step reasoning, 3) Confidence assessment, 4) Alternative perspectives"
        elif task_type == TaskType.EXPERIMENTAL:
            enhanced_prompt += "Please include: 1) Experimental design, 2) Control groups, 3) Statistical considerations, 4) Expected outcomes, 5) Potential limitations"
        elif task_type == TaskType.HYPOTHESIS:
            enhanced_prompt += "Please provide: 1) Multiple novel hypotheses, 2) Testability assessment, 3) Required evidence, 4) Potential implications"
        elif task_type == TaskType.SAFETY:
            enhanced_prompt += "Please assess: 1) Potential risks, 2) Ethical considerations, 3) Safety measures, 4) Monitoring requirements"
        
        return enhanced_prompt
    
    async def _call_model(self, 
                         model: str, 
                         prompt: str, 
                         temperature: float, 
                         max_tokens: int) -> Dict[str, Any]:
        """Call the appropriate model with the given parameters"""
        
        provider = self.providers['openai']
        
        # For now, use synchronous call and wrap in async
        try:
            response = provider.generate(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response
        except Exception as e:
            self.logger.error(f"Error calling model {model}: {str(e)}")
            return {'content': f'Error: {str(e)}', 'cost': 0.0}
    
    def _process_response(self, 
                         response: Dict[str, Any], 
                         task_type: TaskType, 
                         config: Dict[str, Any]) -> LLMResponse:
        """Process raw model response into structured format"""
        
        content = response.get('content', '')
        
        # Extract confidence if mentioned in response
        confidence = self._extract_confidence(content)
        
        # Extract reasoning/methodology
        reasoning = self._extract_reasoning(content, task_type)
        
        # Extract sources if mentioned
        sources = self._extract_sources(content)
        
        return LLMResponse(
            content=content,
            confidence=confidence,
            reasoning=reasoning,
            sources=sources,
            metadata={
                'task_type': task_type.value,
                'model_config': config,
                'response_length': len(content)
            },
            timestamp=datetime.now(),
            model_used=config['model'],
            cost=response.get('cost', 0.0)
        )
    
    def _extract_confidence(self, content: str) -> float:
        """Extract confidence score from response content"""
        # Simple heuristic - can be enhanced with ML
        confidence_keywords = {
            'certain': 0.95, 'confident': 0.9, 'likely': 0.8, 
            'probable': 0.75, 'possible': 0.6, 'uncertain': 0.4,
            'unlikely': 0.3, 'doubtful': 0.2
        }
        
        content_lower = content.lower()
        for keyword, score in confidence_keywords.items():
            if keyword in content_lower:
                return score
        
        return 0.7  # Default moderate confidence
    
    def _extract_reasoning(self, content: str, task_type: TaskType) -> str:
        """Extract reasoning or methodology from response"""
        # Look for reasoning indicators
        reasoning_markers = [
            "because", "therefore", "thus", "hence", "methodology",
            "approach", "reasoning", "analysis", "logic"
        ]
        
        lines = content.split('\n')
        reasoning_lines = []
        
        for line in lines:
            if any(marker in line.lower() for marker in reasoning_markers):
                reasoning_lines.append(line.strip())
        
        return '\n'.join(reasoning_lines) if reasoning_lines else "Implicit reasoning"
    
    def _extract_sources(self, content: str) -> List[str]:
        """Extract potential sources or references from content"""
        # Simple extraction - can be enhanced
        sources = []
        lines = content.split('\n')
        
        for line in lines:
            if any(indicator in line.lower() for indicator in ['source:', 'reference:', 'ref:', 'based on']):
                sources.append(line.strip())
        
        return sources
    
    def _update_context(self, context: ResearchContext, response: LLMResponse):
        """Update research context with new findings"""
        context_key = f"{context.domain}_{context.topic}"
        
        if context_key not in self.conversation_history:
            self.conversation_history[context_key] = []
        
        self.conversation_history[context_key].append({
            'timestamp': response.timestamp,
            'response': asdict(response),
            'context': asdict(context)
        })
    
    async def generate_research_hypothesis(self, 
                                         domain: str, 
                                         research_question: str,
                                         background: List[str] = None) -> LLMResponse:
        """Generate research hypotheses for a given domain and question"""
        
        context = ResearchContext(
            domain=domain,
            topic=research_question,
            previous_findings=background or [],
            constraints={},
            priority="high",
            budget_remaining=50000.0
        )
        
        prompt = f"""
        Generate 3-5 novel, testable hypotheses for the research question: "{research_question}"
        
        For each hypothesis, provide:
        1. Clear statement of the hypothesis
        2. Testability assessment
        3. Required evidence/experiments
        4. Potential implications
        5. Innovation level (1-10)
        
        Focus on hypotheses that could lead to significant scientific breakthroughs.
        """
        
        return await self.route_task(TaskType.HYPOTHESIS, prompt, context)
    
    async def design_experiment(self, 
                               hypothesis: str, 
                               domain: str,
                               constraints: Dict[str, Any] = None) -> LLMResponse:
        """Design experiments to test a given hypothesis"""
        
        context = ResearchContext(
            domain=domain,
            topic=hypothesis,
            previous_findings=[],
            constraints=constraints or {},
            priority="high",
            budget_remaining=30000.0
        )
        
        prompt = f"""
        Design a comprehensive experimental protocol to test this hypothesis: "{hypothesis}"
        
        Include:
        1. Experimental design (controls, variables, etc.)
        2. Materials and methods
        3. Data collection protocol
        4. Statistical analysis plan
        5. Timeline and resource requirements
        6. Potential limitations and mitigation strategies
        7. Expected outcomes and interpretation
        
        Ensure the design is rigorous, feasible, and ethically sound.
        """
        
        return await self.route_task(TaskType.EXPERIMENTAL, prompt, context)
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for the LLM manager"""
        total_calls = sum(len(history) for history in self.conversation_history.values())
        
        task_type_counts = {}
        total_cost = 0.0
        
        for history in self.conversation_history.values():
            for entry in history:
                task_type = entry['response']['metadata']['task_type']
                task_type_counts[task_type] = task_type_counts.get(task_type, 0) + 1
                total_cost += entry['response']['cost']
        
        return {
            'total_calls': total_calls,
            'task_type_distribution': task_type_counts,
            'total_cost': total_cost,
            'active_contexts': len(self.active_contexts),
            'conversation_threads': len(self.conversation_history)
        } 