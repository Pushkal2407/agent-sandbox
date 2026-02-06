"""Model-agnostic interface for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ToolInvocation:
    """Normalized tool call schema across all model providers."""
    name: str
    args: Dict[str, Any]
    call_id: Optional[str] = None


class BaseModelClient(ABC):
    """Abstract interface for LLM model clients. All providers must implement chat()."""
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Tuple[Optional[str], List[ToolInvocation]]:
        """
        Send chat completion request.
        
        Returns: (content, tool_calls) where content is text response,
        tool_calls is list of ToolInvocation objects.
        """
        pass

