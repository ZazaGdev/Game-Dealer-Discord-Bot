# api/http.py
from __future__ import annotations
import asyncio
import random
from typing import Any, Dict, Optional
import aiohttp

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10)  # seconds

class HttpClient:
    def __init__(self, *, headers: Optional[Dict[str, str]] = None, timeout: aiohttp.ClientTimeout | None = None):
        self._session: aiohttp.ClientSession | None = None
        self._headers = headers or {}
        self._timeout = timeout or DEFAULT_TIMEOUT

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout, headers=self._headers)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_json(self, url: str, *, params: Optional[Dict[str, Any]] = None, retries: int = 3) -> Any:
        delay = 0.5
        for attempt in range(1, retries + 1):
            try:
                async with self.session.get(url, params=params) as resp:
                    # Handle server errors with better messages
                    if resp.status >= 500:
                        error_msg = f"Server error {resp.status}"
                        if resp.status == 502:
                            error_msg = "API service temporarily unavailable (Bad Gateway)"
                        elif resp.status == 503:
                            error_msg = "API service temporarily unavailable (Service Unavailable)"
                        elif resp.status == 504:
                            error_msg = "API request timed out (Gateway Timeout)"
                        raise aiohttp.ClientResponseError(resp.request_info, resp.history, status=resp.status, message=error_msg)
                    
                    resp.raise_for_status()
                    
                    # Check content type before parsing JSON
                    if 'application/json' not in resp.content_type:
                        text_content = await resp.text()
                        if resp.status == 200 and not text_content.strip():
                            raise ValueError("API returned empty response")
                        raise ValueError(f"API returned non-JSON content (Content-Type: {resp.content_type})")
                    
                    json_data = await resp.json()
                    
                    # Handle case where JSON parsing returns None (empty response)
                    if json_data is None:
                        raise ValueError("API returned null/empty JSON response")
                        
                    return json_data
                    
            except aiohttp.ClientResponseError as e:
                if 400 <= e.status < 500:
                    raise  # don't retry client errors
                # For server errors, retry with backoff
                if attempt == retries:
                    raise
            except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
                if attempt == retries:
                    raise
                # capped exponential backoff with jitter
                await asyncio.sleep(delay + random.random() * 0.25)
                delay = min(delay * 2, 4.0)
            except ValueError as e:
                # Don't retry JSON parsing errors or empty responses
                raise
