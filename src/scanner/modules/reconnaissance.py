import nmap
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ReconConfig:
    """Configuration for reconnaissance scanning"""
    enabled: bool = True
    target_range: str = "127.0.0.1"
    scan_type: str = "basic"
    ports: str = "80,443"
    aggressive: bool = False
    service_detection: bool = True

class ReconnaissanceScanner:
    def __init__(self, config: ReconConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.nm = nmap.PortScanner()
        
    def scan(self) -> Dict:
        try:
            args = f"-p{self.config.ports}"
            if self.config.service_detection:
                args += " -sV"
            if not self.config.aggressive:
                args += " -T3"
                
            self.nm.scan(
                self.config.target_range,
                arguments=args
            )
            
            return self._parse_results()
            
        except Exception as e:
            self.logger.error(f"Reconnaissance scan failed: {str(e)}")
            return {'error': str(e)}
            
    def _parse_results(self) -> Dict:
        results = {
            'hosts': [],
            'services': []
        }
        
        for host in self.nm.all_hosts():
            host_info = {
                'address': host,
                'status': self.nm[host].state(),
                'open_ports': []
            }
            
            for proto in self.nm[host].all_protocols():
                ports = self.nm[host][proto].keys()
                for port in ports:
                    service = self.nm[host][proto][port]
                    host_info['open_ports'].append({
                        'port': port,
                        'service': service.get('name', ''),
                        'version': service.get('version', '')
                    })
                    
            results['hosts'].append(host_info)
            
        return results 