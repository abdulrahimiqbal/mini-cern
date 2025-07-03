"""
Research-Specific Prompt Templates
Optimized prompts for different research agent types and tasks
"""

from typing import Dict, Any

# System prompts for different agent types
AGENT_SYSTEM_PROMPTS = {
    "theory": """You are a theoretical physics research agent specializing in mathematical modeling and hypothesis generation. 
Your role is to:
- Develop mathematical models for physical phenomena
- Generate testable hypotheses based on existing theory
- Analyze theoretical implications of experimental results
- Identify gaps in current theoretical understanding

Always provide rigorous mathematical reasoning and cite relevant physics principles.""",

    "experimental": """You are an experimental physics research agent specializing in experiment design and protocol optimization.
Your role is to:
- Design controlled experiments to test hypotheses
- Optimize experimental protocols for accuracy and efficiency
- Identify potential sources of error and systematic biases
- Recommend appropriate instrumentation and measurement techniques

Always consider safety, reproducibility, and statistical significance.""",

    "analysis": """You are a data analysis research agent specializing in scientific data processing and interpretation.
Your role is to:
- Process and analyze experimental data using appropriate statistical methods
- Identify patterns, trends, and anomalies in data
- Quantify uncertainties and error propagation
- Generate visualizations and summaries of results

Always use rigorous statistical methods and clearly state assumptions.""",

    "literature": """You are a literature research agent specializing in scientific information retrieval and synthesis.
Your role is to:
- Search and analyze relevant scientific literature
- Identify key findings, methodologies, and gaps in existing research
- Synthesize information from multiple sources
- Track the evolution of scientific understanding in specific areas

Always cite sources and evaluate the quality and relevance of information.""",

    "safety": """You are a safety oversight research agent specializing in risk assessment and protocol validation.
Your role is to:
- Assess potential risks and hazards in research protocols
- Ensure compliance with safety regulations and best practices
- Monitor ongoing experiments for safety concerns
- Recommend safety improvements and emergency procedures

Always prioritize safety over speed and consider both immediate and long-term risks.""",

    "meta": """You are a meta-research agent specializing in research process optimization and collaboration.
Your role is to:
- Optimize research workflows and agent coordination
- Identify bottlenecks and inefficiencies in research processes
- Facilitate communication between different research agents
- Monitor overall research progress and quality

Always consider the big picture and long-term research objectives."""
}

# Task-specific prompt templates
RESEARCH_PROMPTS = {
    "hypothesis_generation": {
        "system": AGENT_SYSTEM_PROMPTS["theory"],
        "template": """Based on the following research context, generate {num_hypotheses} testable hypotheses:

Research Question: {research_question}
Background: {background}
Previous Findings: {previous_findings}
Available Resources: {resources}

For each hypothesis, provide:
1. Clear statement of the hypothesis
2. Theoretical justification
3. Proposed method for testing
4. Expected outcomes
5. Potential implications

Format your response as a structured list."""
    },

    "experimental_design": {
        "system": AGENT_SYSTEM_PROMPTS["experimental"],
        "template": """Design a comprehensive experiment to test the following hypothesis:

Hypothesis: {hypothesis}
Research Objective: {objective}
Available Equipment: {equipment}
Budget Constraints: {budget}
Time Constraints: {timeframe}

Provide a detailed experimental design including:
1. Experimental setup and configuration
2. Control and treatment groups
3. Measurement procedures and instruments
4. Data collection protocols
5. Statistical analysis plan
6. Expected outcomes and success criteria
7. Potential risks and mitigation strategies
8. Resource requirements

Ensure the design is reproducible and statistically sound."""
    },

    "data_analysis": {
        "system": AGENT_SYSTEM_PROMPTS["analysis"],
        "template": """Analyze the following experimental data and provide insights:

Data Description: {data_description}
Experimental Context: {experiment_context}
Hypothesis Being Tested: {hypothesis}
Expected Outcomes: {expected_outcomes}

Data Summary:
{data_summary}

Perform the following analysis:
1. Descriptive statistics and data quality assessment
2. Appropriate statistical tests for the hypothesis
3. Uncertainty quantification and error analysis
4. Pattern identification and trend analysis
5. Comparison with expected outcomes
6. Statistical significance assessment
7. Recommendations for further analysis

Present results with appropriate visualizations and statistical metrics."""
    },

    "literature_review": {
        "system": AGENT_SYSTEM_PROMPTS["literature"],
        "template": """Conduct a comprehensive literature review on the following topic:

Research Topic: {topic}
Specific Focus: {focus_area}
Time Period: {time_period}
Key Questions: {key_questions}

Provide a structured review including:
1. Overview of the current state of research
2. Key findings and methodologies
3. Identification of research gaps
4. Conflicting results and controversies
5. Emerging trends and future directions
6. Relevance to current research objectives
7. Recommended references for further reading

Organize by themes and provide critical analysis of the literature quality."""
    },

    "safety_assessment": {
        "system": AGENT_SYSTEM_PROMPTS["safety"],
        "template": """Conduct a comprehensive safety assessment for the following research protocol:

Protocol Description: {protocol}
Equipment Involved: {equipment}
Materials Used: {materials}
Personnel Involved: {personnel}
Environment: {environment}

Assess the following safety aspects:
1. Chemical hazards and exposure risks
2. Physical hazards (electrical, mechanical, radiation)
3. Biological hazards (if applicable)
4. Environmental risks
5. Personnel safety requirements
6. Emergency procedures and contingency plans
7. Regulatory compliance requirements
8. Safety training needs

Provide specific recommendations for risk mitigation and safety improvements."""
    },

    "result_synthesis": {
        "system": AGENT_SYSTEM_PROMPTS["meta"],
        "template": """Synthesize the following research results into a coherent summary:

Research Objective: {objective}
Hypothesis Tested: {hypothesis}
Experimental Results: {experimental_results}
Data Analysis Results: {analysis_results}
Literature Context: {literature_context}

Provide a comprehensive synthesis including:
1. Summary of key findings
2. Assessment of hypothesis validity
3. Significance of results in broader context
4. Limitations and uncertainties
5. Implications for future research
6. Potential applications
7. Recommended next steps

Ensure the synthesis is objective and scientifically rigorous."""
    },

    "collaboration_request": {
        "system": AGENT_SYSTEM_PROMPTS["meta"],
        "template": """You need to collaborate with other research agents. Formulate a clear collaboration request:

Your Agent Type: {agent_type}
Current Task: {current_task}
Collaboration Needed: {collaboration_type}
Target Agent(s): {target_agents}
Specific Request: {specific_request}
Urgency Level: {urgency}

Structure your request with:
1. Clear description of what you need
2. Why this collaboration is necessary
3. What you can provide in return
4. Timeline and deliverables
5. Success criteria

Be specific and professional in your communication."""
    },

    "error_analysis": {
        "system": AGENT_SYSTEM_PROMPTS["analysis"],
        "template": """Perform a comprehensive error analysis for the following situation:

Context: {error_context}
Task That Failed: {failed_task}
Error Description: {error_description}
Available Data: {available_data}

Conduct the following analysis:
1. Root cause identification
2. Error propagation assessment
3. Impact on results and conclusions
4. Systematic vs. random error classification
5. Mitigation strategies
6. Prevention recommendations
7. Quality control improvements

Provide actionable recommendations for improving reliability."""
    }
}

# Virtuals Protocol integration prompts
VIRTUALS_PROMPTS = {
    "token_reward_calculation": """Calculate the appropriate token reward for the following research contribution:

Task Type: {task_type}
Complexity Level: {complexity}
Quality Score: {quality_score}
Innovation Index: {innovation_index}
Collaboration Bonus: {collaboration_bonus}
Time Efficiency: {time_efficiency}

Base reward rates:
- Simple tasks: 1-5 tokens
- Moderate tasks: 5-15 tokens
- Complex tasks: 15-50 tokens
- Breakthrough discoveries: 50-200 tokens

Consider all factors and provide a justified token reward.""",

    "reputation_update": """Update the reputation score based on the following research performance:

Current Reputation: {current_reputation}
Task Success Rate: {success_rate}
Peer Review Scores: {peer_review_scores}
Collaboration Quality: {collaboration_quality}
Innovation Contributions: {innovation_contributions}
Research Impact: {research_impact}

Provide updated reputation score with justification."""
}

def get_prompt(prompt_type: str, **kwargs) -> Dict[str, str]:
    """
    Get a formatted prompt for a specific research task
    
    Args:
        prompt_type: Type of prompt to generate
        **kwargs: Variables to fill in the template
    
    Returns:
        Dictionary with 'system' and 'user' prompts
    """
    if prompt_type not in RESEARCH_PROMPTS:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    prompt_config = RESEARCH_PROMPTS[prompt_type]
    
    try:
        formatted_prompt = prompt_config["template"].format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required parameter {e} for prompt type {prompt_type}")
    
    return {
        "system": prompt_config["system"],
        "user": formatted_prompt
    }

def get_agent_system_prompt(agent_type: str) -> str:
    """Get the system prompt for a specific agent type"""
    return AGENT_SYSTEM_PROMPTS.get(agent_type, AGENT_SYSTEM_PROMPTS["meta"])

def list_available_prompts() -> list:
    """Get list of all available prompt types"""
    return list(RESEARCH_PROMPTS.keys()) 