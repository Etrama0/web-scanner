import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
from web_scanner.config.scanner_config import ScannerConfig

@pytest.fixture
def scanner():
    config = ScannerConfig()
    return VulnerabilityScanner(config)

def test_scanner_initialization(scanner):
    assert scanner is not None
    assert scanner.patterns is not None
    assert 'xss' in scanner.patterns
    assert 'sqli' in scanner.patterns

@pytest.mark.asyncio
async def test_basic_scan(scanner):
    results = await scanner.scan("http://example.com")
    assert results is not None
    assert 'findings' in results
    assert 'scan_duration' in results
