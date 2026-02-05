"""
Model client abstractions and implementations.

This package provides the model abstraction layer for AgentBox, allowing
model-agnostic agent execution with support for multiple LLM providers.
"""

from .base import BaseModelClient, ToolInvocation
from .openai_client import OpenAIClient

__all__ = ["BaseModelClient", "ToolInvocation", "OpenAIClient"]
