"""
Agent Framework Exceptions
Custom exceptions for agent operations and error handling
"""

class AgentError(Exception):
    """Base exception for all agent-related errors"""
    def __init__(self, message: str, agent_id: str = None, error_code: str = None):
        self.agent_id = agent_id
        self.error_code = error_code
        super().__init__(message)

class AgentInitializationError(AgentError):
    """Raised when agent initialization fails"""
    pass

class TaskExecutionError(AgentError):
    """Raised when agent fails to execute a task"""
    def __init__(self, message: str, agent_id: str = None, task_id: str = None, error_code: str = None):
        self.task_id = task_id
        super().__init__(message, agent_id, error_code)

class CommunicationError(AgentError):
    """Raised when agent communication fails"""
    def __init__(self, message: str, sender_id: str = None, recipient_id: str = None, error_code: str = None):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        super().__init__(message, error_code=error_code)

class LLMIntegrationError(AgentError):
    """Raised when LLM integration fails"""
    def __init__(self, message: str, provider: str = None, model: str = None, error_code: str = None):
        self.provider = provider
        self.model = model
        super().__init__(message, error_code=error_code)

class AgentResourceError(AgentError):
    """Raised when agent lacks required resources"""
    pass

class VirtualsProtocolError(AgentError):
    """Raised when Virtuals Protocol integration fails"""
    def __init__(self, message: str, operation: str = None, error_code: str = None):
        self.operation = operation
        super().__init__(message, error_code=error_code)

class AgentTimeoutError(AgentError):
    """Raised when agent operation times out"""
    def __init__(self, message: str, timeout_seconds: float = None, agent_id: str = None):
        self.timeout_seconds = timeout_seconds
        super().__init__(message, agent_id=agent_id)

class AgentCapabilityError(AgentError):
    """Raised when agent lacks required capability for a task"""
    def __init__(self, message: str, required_capability: str = None, agent_id: str = None):
        self.required_capability = required_capability
        super().__init__(message, agent_id=agent_id) 