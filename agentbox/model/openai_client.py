"""
OpenAI implementation of the BaseModelClient interface.

This module provides an adapter for OpenAI's chat completion API with full
support for tool calling and message formatting.
"""

import os
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

from .base import BaseModelClient, ToolInvocation


class OpenAIClient(BaseModelClient):
    """
    OpenAI-specific implementation of the model client interface.
    
    This client handles communication with OpenAI's chat completion API,
    including proper message formatting, tool schema conversion, and
    response parsing.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var
            model: Model identifier to use (default: gpt-4o-mini)
            
        Raises:
            ValueError: If no API key is provided and OPENAI_API_KEY env var is not set
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided either as argument or via "
                "OPENAI_API_KEY environment variable"
            )
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
    
    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Tuple[Optional[str], List[ToolInvocation]]:
        """
        Send a chat completion request to OpenAI.
        
        Args:
            messages: List of chat messages
            tools: Optional list of tool schemas
            **kwargs: Additional OpenAI-specific parameters (temperature, max_tokens, etc.)
            
        Returns:
            Tuple of (content, tool_calls)
        """
        # Prepare the request parameters
        request_params: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        # Add tools if provided
        if tools:
            request_params["tools"] = tools
        
        # Make the API request
        try:
            response = self.client.chat.completions.create(**request_params)
        except Exception as e:
            raise Exception(f"OpenAI API request failed: {str(e)}") from e
        
        # Extract the assistant's message
        choice = response.choices[0]
        message = choice.message
        
        # Parse text content
        content = message.content if message.content else None
        
        # Parse tool calls
        tool_calls: List[ToolInvocation] = []
        if message.tool_calls:
            for tool_call in message.tool_calls:
                # OpenAI tool calls have: id, type, function.name, function.arguments
                import json
                tool_calls.append(
                    ToolInvocation(
                        name=tool_call.function.name,
                        args=json.loads(tool_call.function.arguments),
                        call_id=tool_call.id
                    )
                )
        
        return content, tool_calls
