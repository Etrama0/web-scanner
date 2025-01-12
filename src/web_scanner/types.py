from dataclasses import dataclass, field
from typing import Optional, Dict, List

@dataclass
class AuthenticationConfig:
    auth_type: str
    username: Optional[str] = None 
    password: Optional[str] = None
    token: Optional[str] = None
    
@dataclass
class BruteForceConfig:
    enabled: bool = False
    wordlist: str = ""
    max_attempts: int = 1000
    
@dataclass 
class ReconConfig:
    enabled: bool = False
    port_scan: bool = True
    service_detection: bool = True

@dataclass
class ModulesConfig:
    """Configuration for optional scanning modules"""
    brute_force: Optional[BruteForceConfig] = None
    reconnaissance: Optional[ReconConfig] = None
    exploit: Optional[Dict] = None

@dataclass
class ScannerConfig:
    """Configuration settings for the scanner"""
    
    # Target settings
    target_url: str = ""
    
    # General settings
    threads: int = 10
    timeout: int = 10
    user_agent: str = 'Mozilla/5.0 (compatible; SecurityScanner/1.0)'
    verify_ssl: bool = False
    
    # Network scan settings
    port_ranges: List[tuple] = field(default_factory=list)
    skip_ports: List[int] = field(default_factory=list)
    
    # Web scan settings
    max_crawl_depth: int = 3
    excluded_paths: List[str] = field(default_factory=list)
    
    # Rate limiting
    requests_per_second: float = 10.0
    burst_size: int = 10
    
    # Proxy settings
    proxy_list: List[Dict] = field(default_factory=list)
    
    # Module configurations
    modules: ModulesConfig = field(default_factory=ModulesConfig)
    
    # Authentication
    authentication: Optional[AuthenticationConfig] = None
