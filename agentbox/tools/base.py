"""Base interface for all AgentBox tools with OpenAI schema generation."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from agentbox.policy import Policy


class SafeTool(ABC):
    """All tools inherit from this class. Provides automatic OpenAI schema generation."""
    
    def __init__(self):
        self.name: str = self._get_name()
        self.description: str = self._get_description()
        self.parameters: Dict[str, Any] = self._get_parameters()
    
    @abstractmethod
    def _get_name(self) -> str:
        pass
    
    @abstractmethod
    def _get_description(self) -> str:
        pass
    
    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        """Return JSON Schema for tool parameters."""
        pass
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Any:
        """Execute the tool with provided arguments."""
        pass
    
    def execute_with_policy(self, args: Dict[str, Any], policy: Optional["Policy"] = None) -> Any:
        """Execute with optional policy validation. Raises PolicyDeniedError if denied."""
        if policy:
            from agentbox.policy import PolicyDeniedError
            
            decision = policy.validate(self.name, args)
            if not decision.allowed:
                raise PolicyDeniedError(decision.reason)
        
        return self.execute(args)
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

