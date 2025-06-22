import httpx
from bs4 import BeautifulSoup
from typing import Optional, Any, Dict, Union
import asyncio

class RequestsScraper:
    def __init__(self, timeout: int = 60000) -> None:
        self.timeout = timeout / 1000
        self.client = None

    async def __aenter__(self) -> 'RequestsScraper':
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            verify=False
        )
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self.client:
            await self.client.aclose()

    async def fetch_html(self, url: str, agent: str, retries: int = 3) -> Optional[str]:
        if not self.client:
            return None

        headers = {
            "User-Agent": agent
        }

        for attempt in range(retries):
            try:
                response = await self.client.get(url, headers=headers)
                response.raise_for_status()

                content = response.text
                html = BeautifulSoup(content, 'html.parser').prettify()

                return html

            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return None

        return None

    async def fetch_json(self, url: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None

        headers = {
            "Accept": "application/json"
        }

        for attempt in range(retries):
            try:
                response = await self.client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data

            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return None

        return None