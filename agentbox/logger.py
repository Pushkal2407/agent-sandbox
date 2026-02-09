"""JSONL audit logging for runtime events."""

import json
from datetime import datetime
from typing import Any, Dict, Optional


class AuditLogger:
    """Logs all runtime events to JSONL file for security audit trail."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file = open(filepath, 'a', encoding='utf-8')
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log single event with timestamp."""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            **data
        }
        self.file.write(json.dumps(event) + "\n")
        self.file.flush()
    
    def log_tool_validation(
        self,
        tool_name: str,
        args: Dict[str, Any],
        allowed: bool,
        reason: str
    ) -> None:
        """Log policy validation decision."""
        self.log_event("tool_validation", {
            "tool_name": tool_name,
            "args": args,
            "allowed": allowed,
            "reason": reason
        })
    
    def log_tool_result(
        self,
        tool_name: str,
        success: bool,
        result: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Log tool execution result."""
        data = {
            "tool_name": tool_name,
            "success": success
        }
        if result:
            data["result"] = result[:200]  # Truncate long results
        if error:
            data["error"] = error
        
        self.log_event("tool_result", data)
    
    def log_runtime_error(self, error: str) -> None:
        """Log runtime-level error."""
        self.log_event("runtime_error", {"error": error})
    
    def close(self) -> None:
        """Close log file."""
        self.file.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
