"""File system tool for reading text files."""

import os
from typing import Any, Dict

from .base import SafeTool


class ReadFileTool(SafeTool):
    
    def _get_name(self) -> str:
        return "read_file"
    
    def _get_description(self) -> str:
        return "Read contents of a text file. Returns the file contents as a string."
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file (absolute or relative)"
                }
            },
            "required": ["path"]
        }
    
    def execute(self, args: Dict[str, Any]) -> str:
        path = args.get("path")
        
        if not path or not isinstance(path, str):
            raise ValueError("Path must be a non-empty string")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        if not os.path.isfile(path):
            raise ValueError(f"Path is not a file: {path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
            
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {path}")
        except UnicodeDecodeError:
            raise Exception(f"Failed to decode {path} as UTF-8. File may be binary.")
        except Exception as e:
            raise Exception(f"Failed to read file {path}: {str(e)}")

