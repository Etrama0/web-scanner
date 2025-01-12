import asyncio
import aiohttp
from typing import Set, List
from urllib.parse import urljoin, urlparse
import logging
from bs4 import BeautifulSoup

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

    async def crawl(self, url: str, max_depth: int = None) -> Set[str]:
        """Main crawl method that returns discovered URLs"""
        if max_depth is None:
            max_depth = self.config.max_crawl_depth
            
        await self.init_session()
        try:
            await self._crawl_recursive(url, 0, max_depth)
            return self.visited_urls
        finally:
            await self.close()

    async def _crawl_recursive(self, url: str, depth: int, max_depth: int) -> None:
        if depth > max_depth or url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        try:
            async with self.session.get(url, verify_ssl=self.config.verify_ssl) as response:
                if response.status == 200:
                    text = await response.text()
                    for link in self._extract_links(text):
                        absolute_url = urljoin(url, link)
                        if self.is_valid_url(absolute_url):
                            await self._crawl_recursive(absolute_url, depth + 1, max_depth)
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {str(e)}")

    def _extract_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        return [a.get('href') for a in soup.find_all('a', href=True)]


class AdvancedCrawler(Crawler):
    """Extended crawler with additional features"""
    
    def __init__(self, base_url: str, max_depth: int = 3, max_workers: int = 10):
        super().__init__({
            'target_url': base_url,
            'max_crawl_depth': max_depth,
            'threads': max_workers,
            'verify_ssl': False,
            'user_agent': 'Mozilla/5.0 (compatible; SecurityScanner/1.0)',
            'excluded_paths': []
        })
        self.max_workers = max_workers

    async def crawl(self, url: str, max_depth: int = None) -> Set[str]:
        """Crawl with concurrent workers"""
        if max_depth is None:
            max_depth = self.config.max_crawl_depth
            
        await self.init_session()
        try:
            tasks = []
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def bounded_crawl(url: str, depth: int):
                async with semaphore:
                    await self._crawl_recursive(url, depth, max_depth)
            
            tasks.append(asyncio.create_task(bounded_crawl(url, 0)))
            await asyncio.gather(*tasks)
            
            return self.visited_urls
        finally:
            await self.close()
