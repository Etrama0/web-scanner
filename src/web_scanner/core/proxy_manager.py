import requests
from typing import Dict, List, Optional
import random
import logging
from dataclasses import dataclass
import aiohttp
import asyncio

@dataclass
class Proxy:
    host: str
    port: int
    protocol: str
    username: Optional[str] = None
    password: Optional[str] = None
    last_used: float = 0
    fail_count: int = 0

class ProxyManager:
    """Manage and rotate proxies for scanning operations"""
    
    def __init__(self, proxy_list: List[Dict] = None):
        self.proxies: List[Proxy] = []
        self.current_index = 0
        self.logger = logging.getLogger(__name__)
        
        if proxy_list:
            self.add_proxies(proxy_list)
            
    def add_proxies(self, proxy_list: List[Dict]):
        """Add proxies to the manager"""
        for proxy_dict in proxy_list:
            proxy = Proxy(
                host=proxy_dict['host'],
                port=proxy_dict['port'],
                protocol=proxy_dict.get('protocol', 'http'),
                username=proxy_dict.get('username'),
                password=proxy_dict.get('password')
            )
            self.proxies.append(proxy)
            
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        proxy_url = f"{proxy.protocol}://"
        if proxy.username and proxy.password:
            proxy_url += f"{proxy.username}:{proxy.password}@"
        proxy_url += f"{proxy.host}:{proxy.port}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }
        
    async def verify_proxies(self):
        """Verify all proxies are working"""
        async def check_proxy(proxy: Proxy):
            proxy_url = f"{proxy.protocol}://"
            if proxy.username and proxy.password:
                proxy_url += f"{proxy.username}:{proxy.password}@"
            proxy_url += f"{proxy.host}:{proxy.port}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        'http://httpbin.org/ip',
                        proxy=proxy_url,
                        timeout=10
                    ) as response:
                        if response.status == 200:
                            return True
            except Exception as e:
                self.logger.warning(f"Proxy verification failed: {proxy_url} - {str(e)}")
                proxy.fail_count += 1
                return False
                
        tasks = [check_proxy(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks)
        
        # Remove failed proxies
        self.proxies = [
            proxy for proxy, result in zip(self.proxies, results)
            if result or proxy.fail_count < 3
        ]
        
    def random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy"""
        if not self.proxies:
            return None
        return self.get_proxy_dict(random.choice(self.proxies))
        
    @staticmethod
    def get_proxy_dict(proxy: Proxy) -> Dict[str, str]:
        """Convert Proxy object to requests-compatible dict"""
        proxy_url = f"{proxy.protocol}://"
        if proxy.username and proxy.password:
            proxy_url += f"{proxy.username}:{proxy.password}@"
        proxy_url += f"{proxy.host}:{proxy.port}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }
