"""HTTP request tool for web interaction."""

from typing import Any, Dict, Optional

import requests

from .base import SafeTool


class WebRequestTool(SafeTool):
    
    def _get_name(self) -> str:
        return "web_request"
    
    def _get_description(self) -> str:
        return "Make HTTP GET/POST requests. Returns status code, headers, and body."
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL including http:// or https://"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST"],
                    "description": "HTTP method"
                },
                "headers": {
                    "type": "object",
                    "description": "Optional HTTP headers",
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
        url = args.get("url")
        method = args.get("method", "GET").upper()
        headers = args.get("headers", {})
        body = args.get("body")
        
        if method not in ["GET", "POST"]:
            raise ValueError(f"Invalid HTTP method: {method}. Must be GET or POST.")
        
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")
        
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        
        try:
            # 10s timeout prevents hanging
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, json=body, timeout=10)
            
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

