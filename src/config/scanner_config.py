from dataclasses import dataclass, field
from typing import List, Dict, Optional
import yaml
import os
from ..scanner.modules.brute_force import BruteForceConfig
from ..scanner.modules.reconnaissance import ReconConfig
from ..utils.authentication_manager import AuthConfig as AuthenticationConfig

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
    
    @classmethod
    def from_yaml(cls, path: str) -> 'ScannerConfig':
        """Load configuration from YAML file"""
        with open(path) as f:
            data = yaml.safe_load(f)
            
        # Process authentication config
        auth_data = data.get('authentication', {})
        auth_config = AuthenticationConfig(**auth_data) if auth_data else None
        
        # Process module configs
        modules_data = data.get('modules', {})
        
        # Setup brute force config
        bf_data = modules_data.get('brute_force', {})
        bf_config = BruteForceConfig(**bf_data) if bf_data else None
        
        # Setup recon config
        recon_data = modules_data.get('reconnaissance', {})
        recon_config = ReconConfig(**recon_data) if recon_data else None
        
        # Create modules config
        modules_config = ModulesConfig(
            brute_force=bf_config,
            reconnaissance=recon_config,
            exploit=modules_data.get('exploit', {})
        )
        
        # Create main config
        config_data = {
            k: v for k, v in data.items() 
            if k not in ['authentication', 'modules']
        }
        config = cls(**config_data)
        config.authentication = auth_config
        config.modules = modules_config
        
        return config 