import asyncio
import aiohttp
from typing import Set, List
from urllib.parse import urljoin, urlparse
import logging

class Crawler:
    def __init__(self, config):
        self.config = config
        self.visited_urls: Set[str] = set()
        self.session = None
        self.logger = logging.getLogger(__name__)

    async def init_session(self):
        headers = {'User-Agent': self.config.user_agent}
        self.session = aiohttp.ClientSession(headers=headers)

    async def close(self):
        if self.session:
            await self.session.close()

    def is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        base_parsed = urlparse(self.config.target_url)
        return parsed.netloc == base_parsed.netloc and \
               not any(path in url for path in self.config.excluded_paths)

    async def crawl_url(self, url: str, depth: int) -> List[str]:
        if depth > self.config.max_crawl_depth or url in self.visited_urls:
            return []
        
        self.visited_urls.add(url)
        found_urls = []

        try:
            async with self.session.get(url, verify_ssl=self.config.verify_ssl) as response:
                if response.status == 200:
                    text = await response.text()
                    # Extract links from response
                    # Basic implementation - should be enhanced with proper HTML parsing
                    for link in self._extract_links(text):
                        absolute_url = urljoin(url, link)
                        if self.is_valid_url(absolute_url):
                            found_urls.append(absolute_url)
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {str(e)}")

        return found_urls

    def _extract_links(self, html: str) -> List[str]:
        # Basic implementation - should be enhanced with proper HTML parsing
        # Consider using beautifulsoup4 or similar
        import re
        href_pattern = 'href=[\'"]?([^\'" >]+)'
        return re.findall(href_pattern, html)

    async def start(self):
        await self.init_session()
        try:
            await self.crawl_url(self.config.target_url, 0)
        finally:
            await self.close()
