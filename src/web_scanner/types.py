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
    target_type: str = "ssh"
    target_host: str = ""
    username: str = ""
    password_list: List[str] = field(default_factory=list)
    port: int = 22
    timeout: int = 3
    max_attempts: int = 100
    requests_per_second: float = 1.0
    
@dataclass 
class ReconConfig:
    enabled: bool = False
    port_scan: bool = True
    service_detection: bool = True

class ExploitConfig:
    """Configuration for exploit scanning module"""
    def __init__(self, enabled: bool = False, exploit_type: str = "rce", payload: str = "echo test"):
        self.enabled = enabled
        self.exploit_type = exploit_type  # Supported types: rce, lfi, xxe
        self.payload = payload  # Test payload to use

@dataclass
class ModulesConfig:
    """Configuration for optional scanning modules"""
    brute_force: Optional[BruteForceConfig] = None
    reconnaissance: Optional[ReconConfig] = None
    exploit: Optional[Dict] = None

@dataclass
class TestConfig:
    """Test configuration settings"""
    server_url: str = "http://testserver"
    server_port: int = 8080
    rate_limit: int = 5
    scan_timeout: int = 10
    username: str = "test_user"
    password: str = "test_pass"

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
    
    # Add validation settings
    min_confidence_score: float = 0.7
    max_false_positives: int = 5
    result_deduplication: bool = True
    
    # Add depth control
    max_urls_per_domain: int = 100
    max_test_duration: int = 300  # seconds
    skip_similar_endpoints: bool = True
    
    # Add test weighting
    test_weights: Dict[str, float] = field(default_factory=lambda: {
        'critical': 1.0,
        'high': 0.8,
        'medium': 0.6,
        'low': 0.4,
        'info': 0.2
    })
    
    # Add test configuration
    test_config: Optional[TestConfig] = None
    
    # Add validation settings that were missing
    test_parallelism: int = 1
    retry_failed_tests: bool = True
    fail_fast: bool = False
    test_timeout: int = 30
