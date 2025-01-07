from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse, quote
import asyncio
import aiohttp
import re
from typing import Set, List, Dict
import logging
from bs4 import BeautifulSoup
import requests

class AdvancedCrawler:
    def __init__(self, base_url: str, max_depth: int = 3, max_workers: int = 5):
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_workers = max_workers
        self.visited_urls = set()
        self.logger = logging.getLogger(__name__)
        
    def _clean_url(self, url: str) -> str:
        """Clean and encode URL properly"""
        try:
            # Remove fragments and default ports
            url = url.split('#')[0]
            url = url.replace(':80/', '/').replace(':443/', '/')
            
            # Parse the URL
            parsed = urlparse(url)
            
            # Skip if no hostname
            if not parsed.netloc:
                return None
                
            # Handle IPv6 addresses
            if '[' in parsed.hostname or ']' in parsed.hostname:
                return None
                
            # Skip non-web protocols
            if parsed.scheme not in ('http', 'https'):
                return None
                
            # Rebuild the URL without fragments
            clean_url = f"{parsed.scheme}://{parsed.netloc.rstrip('/')}{parsed.path}"
            if parsed.query:
                clean_url += f"?{parsed.query}"
            return clean_url
            
        except Exception as e:
            self.logger.error(f"Error cleaning URL {url}: {str(e)}")
            return None
            
    async def crawl(self, url: str, max_depth: int = 2) -> List[str]:
        """Crawl the website starting from the given URL"""
        if not url or max_depth < 0:
            return []
            
        discovered_urls = set()
        to_visit = set([url])
        current_depth = 0
        
        try:
            async with aiohttp.ClientSession() as session:
                while to_visit and current_depth <= max_depth:
                    current_batch = list(to_visit)[:10]  # Process max 10 URLs per depth
                    to_visit.clear()
                    
                    # Process URLs in parallel
                    tasks = []
                    for current_url in current_batch:
                        if current_url not in self.visited_urls:
                            task = asyncio.create_task(
                                self._process_url(session, current_url, discovered_urls, to_visit)
                            )
                            tasks.append(task)
                            
                    if tasks:
                        await asyncio.gather(*tasks)
                    
                    current_depth += 1
                    
                    # Early exit if we have enough URLs
                    if len(discovered_urls) >= 20:  # Limit total URLs discovered
                        break
                    
        except Exception as e:
            self.logger.error(f"Crawling error: {str(e)}")
            
        return list(discovered_urls)
            
    async def _process_url(self, session: aiohttp.ClientSession, url: str, 
                          discovered_urls: Set[str], to_visit: Set[str]):
        """Process a single URL"""
        clean_url = self._clean_url(url)
        if not clean_url or clean_url in self.visited_urls:
            return
            
        self.visited_urls.add(clean_url)
        
        try:
            async with session.get(clean_url, ssl=False) as response:
                if response.status == 200:
                    discovered_urls.add(clean_url)
                    
                    # Only process HTML responses
                    if 'text/html' in response.headers.get('Content-Type', ''):
                        text = await response.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        # Process limited number of links
                        for link in soup.find_all('a', href=True)[:20]:  # Limit links per page
                            href = link['href']
                            if href.startswith(('http://', 'https://', '/')):  # Only process absolute URLs and root-relative paths
                                full_url = urljoin(clean_url, href)
                                clean_full_url = self._clean_url(full_url)
                                
                                if clean_full_url and clean_full_url.startswith(self.base_url):
                                    to_visit.add(clean_full_url)
                                
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {str(e)}")