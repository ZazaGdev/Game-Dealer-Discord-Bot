# utils/api_health.py
import asyncio
import aiohttp
from typing import Dict, Any
import logging

class APIHealthChecker:
    """Simple utility to check ITAD API health status"""
    
    def __init__(self):
        self.base_url = "https://api.isthereanydeal.com"
    
    async def check_api_status(self) -> Dict[str, Any]:
        """Check if ITAD API is responding properly"""
        status = {
            "available": False,
            "status_code": None,
            "content_type": None,
            "error_message": None,
            "response_time_ms": None
        }
        
        try:
            import time
            start_time = time.time()
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Try a simple API endpoint
                test_url = f"{self.base_url}/v01/game/plain/"
                params = {"key": "test", "title": "Test Game"}
                
                async with session.get(test_url, params=params) as response:
                    end_time = time.time()
                    status["response_time_ms"] = int((end_time - start_time) * 1000)
                    status["status_code"] = response.status
                    status["content_type"] = response.content_type
                    
                    if response.status == 200:
                        # Check if we get JSON back (even if it's an error response)
                        if 'application/json' in response.content_type:
                            status["available"] = True
                        else:
                            status["error_message"] = f"API returned non-JSON content: {response.content_type}"
                    elif response.status == 403:
                        # API key error is still a "healthy" API response
                        status["available"] = True
                        status["error_message"] = "API key required (but API is responding)"
                    elif response.status >= 500:
                        status["error_message"] = f"Server error: HTTP {response.status}"
                        if response.status == 502:
                            status["error_message"] += " (Bad Gateway - service may be down)"
                    else:
                        status["error_message"] = f"HTTP {response.status}"
                        
        except asyncio.TimeoutError:
            status["error_message"] = "Request timeout (>10s)"
        except aiohttp.ClientConnectionError as e:
            status["error_message"] = f"Connection error: {str(e)}"
        except Exception as e:
            status["error_message"] = f"Unexpected error: {str(e)}"
            
        return status
    
    def format_status_message(self, status: Dict[str, Any]) -> str:
        """Format status check result into a readable message"""
        if status["available"]:
            msg = "✅ ITAD API is responding normally"
            if status["response_time_ms"]:
                msg += f" (Response time: {status['response_time_ms']}ms)"
            return msg
        else:
            msg = "❌ ITAD API is not available"
            if status["error_message"]:
                msg += f": {status['error_message']}"
            if status["status_code"]:
                msg += f" [HTTP {status['status_code']}]"
            return msg

async def quick_api_check() -> None:
    """Standalone function for quick API health check"""
    checker = APIHealthChecker()
    status = await checker.check_api_status()
    print(checker.format_status_message(status))

if __name__ == "__main__":
    asyncio.run(quick_api_check())