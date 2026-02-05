"""
Base abstractions for model clients.

This module defines the model-agnostic interface that all LLM providers must implement,
ensuring consistent behavior across different model backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ToolInvocation:
    """
    Normalized schema for tool calls across all model providers.
    
    All model-specific tool call formats must be converted to this schema
    to ensure consistent handling throughout the runtime.
    
    Attributes:
        name: The name of the tool to invoke
        args: Dictionary of arguments to pass to the tool
        call_id: Optional identifier for tracking this specific tool call
    """
    name: str
    args: Dict[str, Any]
    call_id: Optional[str] = None


class BaseModelClient(ABC):
    """
    Abstract interface for LLM model clients.
    
    This interface defines the contract that all model providers (OpenAI, Anthropic, etc.)
    must implement to integrate with AgentBox. It ensures model-agnostic operation
    while supporting tool calling capabilities.
    """
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Tuple[Optional[str], List[ToolInvocation]]:
        """
        Send a chat completion request to the model.
        
        Args:
            messages: List of chat messages in the format:
                [{"role": "user"|"assistant"|"system", "content": str}, ...]
            tools: Optional list of tool schemas the model can invoke
            **kwargs: Additional model-specific parameters
            
        Returns:
            A tuple of (content, tool_calls) where:
                - content: The text response from the model (None if only tool calls)
                - tool_calls: List of ToolInvocation objects for any tools the model wants to call
                
        Raises:
            Exception: If the API request fails or returns an error
        """
        pass
