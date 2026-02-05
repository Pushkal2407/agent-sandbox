"""
Web request tool for making HTTP requests.

This tool allows agents to make GET and POST requests to web URLs
with proper error handling and response parsing.
"""

from typing import Any, Dict, Optional

import requests

from .base import SafeTool


class WebRequestTool(SafeTool):
    """
    Tool for making HTTP requests to web URLs.
    
    Supports GET and POST methods with optional headers and body.
    Returns structured response data including status code, headers, and body.
    """
    
    def _get_name(self) -> str:
        return "web_request"
    
    def _get_description(self) -> str:
        return (
            "Make HTTP requests to web URLs. Supports GET and POST methods. "
            "Returns the response status code, headers, and body content."
        )
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to make the request to (including http:// or https://)"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST"],
                    "description": "HTTP method to use (GET or POST)"
                },
                "headers": {
                    "type": "object",
                    "description": "Optional HTTP headers to include in the request",
                    "additionalProperties": {"type": "string"}
                },
                "body": {
                    "type": "object",
                    "description": "Optional JSON body for POST requests"
                }
            },
            "required": ["url", "method"]
        }
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an HTTP request.
        
        Args:
            args: Dictionary containing:
                - url (str): Target URL
                - method (str): HTTP method (GET or POST)
                - headers (dict, optional): HTTP headers
                - body (dict, optional): Request body for POST
                
        Returns:
            Dictionary containing:
                - status_code (int): HTTP status code
                - headers (dict): Response headers
                - body (str): Response body content
                
        Raises:
            ValueError: If method is not GET or POST
            Exception: If the request fails
        """
        url = args.get("url")
        method = args.get("method", "GET").upper()
        headers = args.get("headers", {})
        body = args.get("body")
        
        # Validate method
        if method not in ["GET", "POST"]:
            raise ValueError(f"Invalid HTTP method: {method}. Must be GET or POST.")
        
        # Validate URL
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")
        
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        
        try:
            # Make the request with a timeout
            if method == "GET":
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=10
                )
            else:  # POST
                response = requests.post(
                    url,
                    headers=headers,
                    json=body,
                    timeout=10
                )
            
            # Return structured response
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text
            }
            
        except requests.exceptions.Timeout:
            raise Exception(f"Request to {url} timed out after 10 seconds")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Failed to connect to {url}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
