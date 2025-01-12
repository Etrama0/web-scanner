import unittest
from web_scanner.config.scanner_config import ScannerConfig
from web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.config = ScannerConfig.from_yaml('tests/test_config.yaml')
        self.scanner = VulnerabilityScanner(self.config)
        
    def test_basic_scan(self):
        # Use a test server or known vulnerable app
        results = self.scanner.scan("http://testserver")
        self.assertIsNotNone(results)
        
    def test_authenticated_scan(self):
        # Test with authentication
        self.config.authentication = {
            'auth_type': 'basic',
            'username': 'test',
            'password': 'test'
        }
        results = self.scanner.scan("http://testserver/protected")
        self.assertIsNotNone(results)
