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
                    if resp.status >= 500:
                        raise aiohttp.ClientResponseError(resp.request_info, resp.history, status=resp.status)
                    resp.raise_for_status()
                    return await resp.json()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt == retries:
                    raise
                # capped exponential backoff with jitter
                await asyncio.sleep(delay + random.random() * 0.25)
                delay = min(delay * 2, 4.0)
