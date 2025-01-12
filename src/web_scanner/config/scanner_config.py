from dataclasses import dataclass, field
from typing import List, Dict, Optional
import yaml
import logging

from ..types import AuthenticationConfig, BruteForceConfig, ReconConfig, ScannerConfig, ModulesConfig

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
    rotate_proxies: bool = False
    proxy_rotation_interval: int = 300  # seconds
    proxy_retry_count: int = 3
    verify_proxies: bool = True
    proxy_verify_timeout: int = 10
    proxy_verify_url: str = "https://www.google.com"
    
    # Module configurations
    modules: ModulesConfig = field(default_factory=ModulesConfig)
    
    # Authentication
    authentication: Optional[AuthenticationConfig] = None
    
    # Report settings
    report_templates: Dict[str, str] = field(default_factory=dict)
    report_output_dir: str = "reports"
    report_format: str = "html"
    template_dir: str = "templates"
    
    def __iter__(self):
        """Make config iterable"""
        for field in self.__dataclass_fields__:
            yield field, getattr(self, field)
    
    def update(self, config_dict: dict) -> None:
        """Update configuration with values from dictionary"""
        if not isinstance(config_dict, dict):
            config_dict = dict(config_dict)
            
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logging.warning(f"Ignoring invalid configuration key: {key}")
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'ScannerConfig':
        """Create instance from dictionary"""
        return cls(**{
            k: v for k, v in config_dict.items() 
            if hasattr(cls, k)
        })

class AuthenticationConfig:
    def __init__(
        self,
        auth_type: str = 'basic',
        username: str = None,
        password: str = None,
        login_url: str = None,
        token_url: str = None,
        client_id: str = None,
        client_secret: str = None,
        scope: str = None
    ):
        self.auth_type = auth_type
        self.username = username
        self.password = password
        self.login_url = login_url
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope

def load_scanner_config(path: str) -> ScannerConfig:
    """Load configuration from YAML file"""
    with open(path) as f:
        data = yaml.safe_load(f)
    
    # Update auth config processing
    auth_data = data.get('authentication', {})
    auth_config = AuthenticationConfig(**auth_data) if auth_data else None
    
    # Process modules data
    modules_data = data.get('modules', {})
    
    # Create config instance
    config_data = {
        k: v for k, v in data.items() 
        if k not in ['authentication', 'modules']
    }
    
    config = ScannerConfig(**config_data)
    config.authentication = auth_config
    config.modules = modules_data
    
    return config
