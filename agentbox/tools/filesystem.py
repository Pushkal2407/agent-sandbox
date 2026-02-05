"""
File system tool for reading files.

This tool allows agents to read text files with proper error handling
and path validation.
"""

import os
from typing import Any, Dict

from .base import SafeTool


class ReadFileTool(SafeTool):
    """
    Tool for reading text files from the file system.
    
    Reads files in UTF-8 encoding and returns their contents as a string.
    Includes validation for file existence and error handling for common issues.
    """
    
    def _get_name(self) -> str:
        return "read_file"
    
    def _get_description(self) -> str:
        return (
            "Read the contents of a text file from the file system. "
            "Returns the file contents as a string."
        )
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to read (absolute or relative)"
                }
            },
            "required": ["path"]
        }
    
    def execute(self, args: Dict[str, Any]) -> str:
        """
        Read a text file from the file system.
        
        Args:
            args: Dictionary containing:
                - path (str): Path to the file to read
                
        Returns:
            String containing the file contents
            
        Raises:
            ValueError: If path is invalid
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file can't be read due to permissions
            Exception: If the file can't be read for other reasons
        """
        path = args.get("path")
        
        # Validate path argument
        if not path or not isinstance(path, str):
            raise ValueError("Path must be a non-empty string")
        
        # Check if file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(path):
            raise ValueError(f"Path is not a file: {path}")
        
        try:
            # Read the file
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
            
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {path}")
        except UnicodeDecodeError:
            raise Exception(
                f"Failed to decode file {path} as UTF-8. "
                "The file may be binary or use a different encoding."
            )
        except Exception as e:
            raise Exception(f"Failed to read file {path}: {str(e)}")
