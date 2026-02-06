"""Policy engine with default-deny security model for tool validation."""

import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import yaml


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str


class Policy:
    """Validates tool calls against YAML-defined rules. Default deny: all tools blocked unless explicitly allowed."""
    
    def __init__(self, policy_data: Dict[str, Any]):
        self.tools = policy_data.get("tools", {})
        self.limits = policy_data.get("limits", {})
        self.max_tool_calls = self.limits.get("max_tool_calls", float('inf'))
        self.max_runtime_seconds = self.limits.get("max_runtime_seconds", float('inf'))
    
    @classmethod
    def load(cls, yaml_path: str) -> "Policy":
        """Load and parse YAML policy file."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Policy file not found: {yaml_path}")
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                policy_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in policy file: {e}")
        
        if not isinstance(policy_data, dict):
            raise ValueError("Policy file must contain a YAML dictionary")
        
        return cls(policy_data)
    
    def validate(self, tool_name: str, tool_args: Dict[str, Any]) -> PolicyDecision:
        """Validate tool call against policy. Returns decision with clear denial reason."""
        if tool_name not in self.tools:
            return PolicyDecision(
                allowed=False,
                reason=f"Tool '{tool_name}' is not in the policy (default deny)"
            )
        
        tool_policy = self.tools[tool_name]
        
        if tool_name == "web_request":
            return self._validate_web_request(tool_args, tool_policy)
        elif tool_name == "read_file":
            return self._validate_read_file(tool_args, tool_policy)
        else:
            return PolicyDecision(
                allowed=False,
                reason=f"No validation logic for tool '{tool_name}'"
            )
    
    def _validate_web_request(self, args: Dict[str, Any], tool_policy: Dict[str, Any]) -> PolicyDecision:
        url = args.get("url", "")
        method = args.get("method", "GET").upper()
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.split(':')[0]  # Remove port
        except Exception:
            return PolicyDecision(allowed=False, reason=f"Invalid URL format: {url}")
        
        allow_domains = tool_policy.get("allow_domains", [])
        
        if "*" not in allow_domains:
            domain_allowed = any(self._domain_matches(domain, allowed) for allowed in allow_domains)
            if not domain_allowed:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Domain '{domain}' not in allow_domains: {allow_domains}"
                )
        
        allow_methods = tool_policy.get("allow_methods", [])
        if method not in allow_methods:
            return PolicyDecision(
                allowed=False,
                reason=f"HTTP method '{method}' not in allow_methods: {allow_methods}"
            )
        
        return PolicyDecision(allowed=True, reason=f"Allowed: domain '{domain}' and method '{method}'")
    
    def _validate_read_file(self, args: Dict[str, Any], tool_policy: Dict[str, Any]) -> PolicyDecision:
        path = args.get("path", "")
        
        if not path:
            return PolicyDecision(allowed=False, reason="No path provided")
        
        normalized_path = os.path.normpath(path)
        allow_paths = tool_policy.get("allow_paths", [])
        
        # Wildcard check
        if "./**" in allow_paths or "**" in allow_paths:
            return PolicyDecision(allowed=True, reason=f"Allowed: wildcard pattern")
        
        # Pattern matching with fnmatch and pathlib
        for pattern in allow_paths:
            normalized_pattern = os.path.normpath(pattern)
            
            if fnmatch.fnmatch(normalized_path, normalized_pattern):
                return PolicyDecision(allowed=True, reason=f"Allowed: path '{path}' matches '{pattern}'")
            
            try:
                if Path(normalized_path).match(normalized_pattern):
                    return PolicyDecision(allowed=True, reason=f"Allowed: path '{path}' matches '{pattern}'")
            except Exception:
                pass
        
        return PolicyDecision(allowed=False, reason=f"Path '{path}' not in allow_paths: {allow_paths}")
    
    def _domain_matches(self, domain: str, pattern: str) -> bool:
        """Subdomain matching: wikipedia.org matches en.wikipedia.org"""
        return domain == pattern or domain.endswith('.' + pattern)


class PolicyDeniedError(Exception):
    pass
