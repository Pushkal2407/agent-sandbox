"""
Base abstractions for safe tool execution.

This module defines the SafeTool interface that all AgentBox tools must implement,
providing a consistent execution model and OpenAI schema generation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class SafeTool(ABC):
    """
    Abstract base class for all AgentBox tools.
    
    All tools must inherit from this class and implement the execute() method.
    The class provides automatic schema generation for OpenAI function calling.
    
    Attributes:
        name: Unique identifier for the tool
        description: Human-readable description for the LLM
        parameters: JSON Schema defining the tool's parameters
    """
    
    def __init__(self):
        """Initialize the tool with its metadata."""
        self.name: str = self._get_name()
        self.description: str = self._get_description()
        self.parameters: Dict[str, Any] = self._get_parameters()
    
    @abstractmethod
    def _get_name(self) -> str:
        """Return the tool's unique identifier."""
        pass
    
    @abstractmethod
    def _get_description(self) -> str:
        """Return the tool's description for the LLM."""
        pass
    
    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        """
        Return the JSON Schema for the tool's parameters.
        
        Returns:
            A dictionary following JSON Schema format with 'type', 'properties',
            and 'required' fields.
        """
        pass
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Any:
        """
        Execute the tool with the provided arguments.
        
        Args:
            args: Dictionary of arguments matching the tool's parameter schema
            
        Returns:
            The result of the tool execution (type depends on the specific tool)
            
        Raises:
            Exception: If the tool execution fails
        """
        pass
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """
        Convert the tool to OpenAI's function calling schema format.
        
        Returns:
            A dictionary in OpenAI's tool schema format with 'type' and 'function' fields.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
