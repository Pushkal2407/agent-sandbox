"""OpenAI implementation of BaseModelClient."""

import os
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

from .base import BaseModelClient, ToolInvocation

from dotenv import load_dotenv

load_dotenv()

class OpenAIClient(BaseModelClient):
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize with API key from argument or OPENAI_API_KEY env var."""
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
        request_params: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        if tools:
            request_params["tools"] = tools
        
        try:
            response = self.client.chat.completions.create(**request_params)
        except Exception as e:
            raise Exception(f"OpenAI API request failed: {str(e)}") from e
        
        choice = response.choices[0]
        message = choice.message
        content = message.content if message.content else None
        
        # Normalize OpenAI's tool_calls to ToolInvocation schema
        tool_calls: List[ToolInvocation] = []
        if message.tool_calls:
            import json
            for tool_call in message.tool_calls:
                tool_calls.append(
                    ToolInvocation(
                        name=tool_call.function.name,
                        args=json.loads(tool_call.function.arguments),
                        call_id=tool_call.id
                    )
                )
        
        return content, tool_calls

