import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import paramiko
import socket
import aiohttp
from urllib.parse import urlparse

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
    enabled: bool = True

class BruteForceModule:
    def __init__(self, config: BruteForceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.timeout = 5
        
    async def check_port(self, host: str, port: int) -> bool:
        """Check if a port is open on the target host"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False

    async def detect_service(self, host: str, port: int) -> str:
        """Detect the service running on a port"""
        common_ports = {
            22: 'SSH',
            21: 'FTP',
            80: 'HTTP',
            443: 'HTTPS',
            3306: 'MySQL',
            5432: 'PostgreSQL'
        }
        return common_ports.get(port, 'Unknown')

    async def run(self, target_url: str) -> List[Dict]:
        findings = []
        parsed_url = urlparse(target_url)
        host = parsed_url.netloc or parsed_url.path
        
        # Remove port from host if present
        if ':' in host:
            host = host.split(':')[0]

        # Only scan services that match the target type
        target_type = getattr(self.config, 'target_type', 'web')
        service_configs = {
            'ssh': {'ports': [22], 'expected': True if target_type == 'ssh' else False},
            'ftp': {'ports': [21], 'expected': True if target_type == 'ftp' else False},
            'web': {'ports': [80, 443], 'expected': True if target_type == 'web' else False}
        }

        # Only scan ports for the specified target type
        target_service = service_configs.get(target_type, {'ports': [], 'expected': False})
        
        for port in target_service['ports']:
            try:
                is_open = await self.check_port(host, port)
                service_name = await self.detect_service(host, port)

                if is_open:
                    # Only test services that match the target type
                    if port == 22 and target_type == 'ssh':
                        ssh_findings = await self.test_ssh_auth(host, port)
                        findings.extend(ssh_findings)
                    elif port in [80, 443] and target_type == 'web':
                        web_findings = await self.test_web_auth(target_url)
                        findings.extend(web_findings)
                    
                    findings.append({
                        'type': 'Service Detection',
                        'severity': 'Info',
                        'url': target_url,
                        'description': f'Found running {service_name} service',
                        'evidence': f'Successfully connected to {host}:{port}',
                        'remediation': 'Ensure service is properly secured'
                    })
                elif target_service['expected']:
                    # Only report unavailable services when they're expected
                    findings.append({
                        'type': 'Expected Service Not Found',
                        'severity': 'Medium',
                        'url': target_url,
                        'description': f'Expected {service_name} service not found on standard port {port}',
                        'evidence': f'Connection attempt to {host}:{port} failed',
                        'remediation': f'Verify {service_name} service is running on the correct port'
                    })

            except Exception as e:
                if target_service['expected']:
                    findings.append({
                        'type': 'Service Check Error',
                        'severity': 'Low',
                        'url': target_url,
                        'description': f'Error checking {service_name} service',
                        'evidence': str(e),
                        'remediation': 'Check network connectivity and service status'
                    })

        return findings

    async def test_ssh_auth(self, host: str, port: int) -> List[Dict]:
        """Test SSH authentication if the port is open"""
        findings = []
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            for password in self.config.password_list[:self.config.max_attempts]:
                try:
                    ssh.connect(
                        host,
                        port=port,
                        username=self.config.username,
                        password=password,
                        timeout=self.config.timeout
                    )
                    findings.append({
                        'type': 'Weak SSH Credentials',
                        'severity': 'Critical',
                        'url': f'ssh://{host}:{port}',
                        'description': f'Successfully authenticated to SSH with weak credentials',
                        'evidence': f'Username: {self.config.username}, Password: {password}',
                        'remediation': 'Change weak SSH credentials and implement strong password policy'
                    })
                    break
                except paramiko.AuthenticationException:
                    continue
                except (socket.error, paramiko.SSHException):
                    break
                finally:
                    ssh.close()
                    
        except Exception as e:
            findings.append({
                'type': 'SSH Test Error',
                'severity': 'Low',
                'url': f'ssh://{host}:{port}',
                'description': 'Error testing SSH authentication',
                'evidence': str(e),
                'remediation': 'Check SSH service configuration'
            })
        
        return findings

    async def test_web_auth(self, url: str) -> List[Dict]:
        """Test web authentication if target is a web service"""
        findings = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 401:
                        findings.append({
                            'type': 'Authentication Required',
                            'severity': 'Info',
                            'url': url,
                            'description': 'Web authentication is required',
                            'evidence': f'HTTP {response.status} response',
                            'remediation': 'Ensure strong authentication mechanisms are in place'
                        })
                    elif response.status == 200:
                        # Check for login forms
                        text = await response.text()
                        if '<form' in text.lower() and ('login' in text.lower() or 'password' in text.lower()):
                            findings.append({
                                'type': 'Login Form Found',
                                'severity': 'Info',
                                'url': url,
                                'description': 'Login form detected on page',
                                'evidence': 'Found HTML form with login/password fields',
                                'remediation': 'Ensure proper brute force protection is implemented'
                            })
        except Exception as e:
            findings.append({
                'type': 'Web Auth Test Error',
                'severity': 'Low',
                'url': url,
                'description': 'Error testing web authentication',
                'evidence': str(e),
                'remediation': 'Check web server accessibility'
            })
        return findings
