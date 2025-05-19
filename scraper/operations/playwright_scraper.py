from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from bs4 import BeautifulSoup
from typing import Optional, Any, Dict, Union
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PlaywrightScraper:
    def __init__(self, headless: bool = True, timeout: int = 60000) -> None:
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.headless: bool = headless
        self.timeout: int = timeout

    async def __aenter__(self) -> 'PlaywrightScraper':
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def fetch_html(self, url: str, agent: str, retries: int = 3) -> Optional[str]:
        if not self.browser:
            logger.error("Browser not initialized")
            return None

        context: Optional[BrowserContext] = None

        for attempt in range(retries):
            try:
                context = await self.browser.new_context(
                    user_agent=agent, 
                    ignore_https_errors=True
                )
                page: Page = await context.new_page()

                # Set a longer timeout for navigation
                await page.goto(url, wait_until='networkidle', timeout=self.timeout)

                # Wait for the page to be fully loaded
                await page.wait_for_load_state('networkidle')

                # Get the page content
                content = await page.content()

                # Parse and prettify the HTML
                html = BeautifulSoup(content, 'html.parser').prettify()

                logger.info(f"Successfully fetched {url}")
                return html

            except Exception as e:
                logger.error(f"Error fetching {url} (attempt {attempt+1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    # Wait before retrying
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None

            finally:
                if context:
                    await context.close()

        return None

    async def fetch_json(self, url: str, agent: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        if not self.browser:
            logger.error("Browser not initialized")
            return None

        context: Optional[BrowserContext] = None

        for attempt in range(retries):
            try:
                context = await self.browser.new_context(
                    user_agent=agent, 
                    ignore_https_errors=True
                )
                page: Page = await context.new_page()

                response = await page.goto(url, wait_until='networkidle', timeout=self.timeout)

                if not response:
                    logger.error(f"No response from {url}")
                    continue

                content_type = response.headers.get('content-type', '')
                if 'application/json' not in content_type:
                    logger.warning(f"Response from {url} is not JSON: {content_type}")

                text = await response.text()

                import json
                data = json.loads(text)

                logger.info(f"Successfully fetched JSON from {url}")
                return data

            except Exception as e:
                logger.error(f"Error fetching JSON from {url} (attempt {attempt+1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to fetch JSON from {url} after {retries} attempts")
                    return None

            finally:
                if context:
                    await context.close()

        return None
