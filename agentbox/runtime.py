"""Agent runtime loop with policy enforcement and budget limits."""

import time
from typing import Any, Dict, List, Optional

from agentbox.model import BaseModelClient
from agentbox.policy import Policy, PolicyDeniedError
from agentbox.tools import SafeTool


class BudgetExceededError(Exception):
    """Raised when budget limits are exceeded."""
    pass


class MaxIterationsError(Exception):
    """Raised when max iterations reached without completion."""
    pass


class AgentRuntime:
    """Orchestrates LLM conversations with tool execution and policy enforcement."""
    
    def __init__(
        self,
        model_client: BaseModelClient,
        tools: List[SafeTool],
        policy: Policy
    ):
        self.model_client = model_client
        self.tools = {tool.name: tool for tool in tools}
        self.policy = policy
    
    def run(
        self,
        messages: List[Dict[str, Any]],
        max_iterations: int = 10
    ) -> str:
        """
        Execute agent runtime loop with policy and budget enforcement.
        
        Returns: Final assistant response content
        """
        start_time = time.time()
        tool_call_count = 0
        
        for iteration in range(max_iterations):
            # Budget enforcement
            elapsed = time.time() - start_time
            if elapsed > self.policy.max_runtime_seconds:
                raise BudgetExceededError(
                    f"Runtime limit exceeded: {elapsed:.1f}s > {self.policy.max_runtime_seconds}s"
                )
            
            if tool_call_count >= self.policy.max_tool_calls:
                raise BudgetExceededError(
                    f"Tool call limit exceeded: {tool_call_count} >= {self.policy.max_tool_calls}"
                )
            
            # Get LLM response
            tool_schemas = [t.to_openai_schema() for t in self.tools.values()]
            content, tool_calls = self.model_client.chat(messages, tools=tool_schemas)
            
            # No tools called → agent is done
            if not tool_calls:
                return content or ""
            
            # Execute tool calls
            tool_results = []
            for tc in tool_calls:
                result = self._execute_tool(tc)
                tool_results.append(result)
                tool_call_count += 1
            
            # Append assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": content,
                "tool_calls": self._format_tool_calls_for_openai(tool_calls)
            })
            
            # Append tool results
            messages.extend(tool_results)
        
        raise MaxIterationsError(f"Max iterations ({max_iterations}) reached without completion")
    
    def _execute_tool(self, tool_invocation) -> Dict[str, Any]:
        """Execute single tool with policy validation."""
        tool_name = tool_invocation.name
        tool_args = tool_invocation.args
        call_id = tool_invocation.call_id
        
        # Check if tool exists
        if tool_name not in self.tools:
            return self._tool_error_result(
                call_id,
                tool_name,
                f"Tool '{tool_name}' not found"
            )
        
        tool = self.tools[tool_name]
        
        # Validate against policy
        decision = self.policy.validate(tool_name, tool_args)
        if not decision.allowed:
            return self._tool_error_result(
                call_id,
                tool_name,
                f"Policy denied: {decision.reason}"
            )
        
        # Execute tool
        try:
            result = tool.execute(tool_args)
            return self._tool_success_result(call_id, tool_name, result)
        except Exception as e:
            return self._tool_error_result(call_id, tool_name, str(e))
    
    def _tool_success_result(
        self,
        call_id: str,
        tool_name: str,
        result: Any
    ) -> Dict[str, Any]:
        """Format successful tool result for OpenAI."""
        # Convert result to string if needed
        if isinstance(result, dict):
            import json
            content = json.dumps(result)
        else:
            content = str(result)
        
        return {
            "role": "tool",
            "tool_call_id": call_id,
            "name": tool_name,
            "content": content
        }
    
    def _tool_error_result(
        self,
        call_id: str,
        tool_name: str,
        error: str
    ) -> Dict[str, Any]:
        """Format tool error for OpenAI."""
        return {
            "role": "tool",
            "tool_call_id": call_id,
            "name": tool_name,
            "content": f'{{"error": "{error}"}}'
        }
    
    def _format_tool_calls_for_openai(self, tool_calls) -> List[Dict[str, Any]]:
        """Convert ToolInvocation list to OpenAI format."""
        import json
        
        formatted = []
        for tc in tool_calls:
            formatted.append({
                "id": tc.call_id,
                "type": "function",
                "function": {
                    "name": tc.name,
                    "arguments": json.dumps(tc.args)
                }
            })
        return formatted
