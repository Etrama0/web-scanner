import logging
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import requests
from urllib.parse import urljoin, urlparse

class AdvancedVulnerabilityScanner:
    """Advanced vulnerability scanning module"""
    
    def __init__(self, config: Dict = None, logger=None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.findings: List[Dict] = []
        
        # Common vulnerability patterns
        self.patterns = {
            'sql_injection': [
                "'", 
                "1' OR '1'='1", 
                "1; DROP TABLE users--",
                "' UNION SELECT NULL--",
            ],
            'xss': [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
            ],
            'lfi': [
                "../../../etc/passwd",
                "....//....//etc/passwd",
                "php://filter/convert.base64-encode/resource=index.php",
            ],
            'sensitive_files': [
                ".env",
                "config.php",
                ".git/config",
                "wp-config.php",
                "phpinfo.php",
            ]
        }

    def test_csrf(self, response, url: str) -> Optional[Dict]:
        """Test for CSRF vulnerabilities"""
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form', method=True)
            
            for form in forms:
                if form.get('method', '').upper() != 'POST':
                    continue
                    
                csrf_found = False
                for input_field in form.find_all('input'):
                    name = input_field.get('name', '').lower()
                    if any(token in name for token in ['csrf', 'token', '_token', 'nonce']):
                        csrf_found = True
                        break
                        
                if not csrf_found:
                    return {
                        'type': 'CSRF',
                        'url': url,
                        'form_action': form.get('action', ''),
                        'severity': 'Medium',
                        'description': 'Form lacks CSRF protection',
                        'evidence': str(form),
                        'remediation': 'Implement CSRF tokens for all POST forms'
                    }
        except Exception as e:
            self.logger.error(f"Error testing CSRF on {url}: {str(e)}")
        return None

    def test_xss(self, response, url: str) -> Optional[Dict]:
        """Test for XSS vulnerabilities"""
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for reflected parameters
            parsed_url = urlparse(url)
            params = parsed_url.query.split('&')
            for param in params:
                if '=' in param:
                    name, value = param.split('=', 1)
                    if value and value in response.text:
                        return {
                            'type': 'Potential XSS',
                            'url': url,
                            'severity': 'High',
                            'description': f'Parameter {name} is reflected in the response',
                            'evidence': f'Parameter: {name}={value}',
                            'remediation': 'Implement proper output encoding'
                        }
                        
            # Check for unsafe attributes
            for tag in soup.find_all(['script', 'img', 'a']):
                for attr in ['src', 'href', 'onerror', 'onload']:
                    if tag.get(attr, '').startswith('javascript:'):
                        return {
                            'type': 'Potential XSS',
                            'url': url,
                            'severity': 'High',
                            'description': f'Unsafe {attr} attribute found',
                            'evidence': str(tag),
                            'remediation': 'Remove or sanitize unsafe JavaScript attributes'
                        }
        except Exception as e:
            self.logger.error(f"Error testing XSS on {url}: {str(e)}")
        return None

    def test_information_disclosure(self, response, url: str) -> Optional[Dict]:
        """Test for information disclosure"""
        try:
            # Check for common sensitive information patterns
            patterns = {
                'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
                'api_key': r'(?i)(api[_-]?key|access[_-]?token)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{32,})',
                'aws_key': r'(?i)AKIA[0-9A-Z]{16}'
            }
            
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, response.text)
                if matches:
                    return {
                        'type': 'Information Disclosure',
                        'url': url,
                        'severity': 'Medium',
                        'description': f'Found potential {pattern_name} disclosure',
                        'evidence': str(matches[:3]),  # Show first 3 matches
                        'remediation': 'Remove or mask sensitive information'
                    }
                    
            # Check for server information in headers
            sensitive_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version', 'X-AspNetMvc-Version']
            for header in sensitive_headers:
                if header in response.headers:
                    return {
                        'type': 'Information Disclosure',
                        'url': url,
                        'severity': 'Low',
                        'description': f'Server information disclosed in {header} header',
                        'evidence': f'{header}: {response.headers[header]}',
                        'remediation': 'Remove or customize server information headers'
                    }
        except Exception as e:
            self.logger.error(f"Error testing information disclosure on {url}: {str(e)}")
        return None

    def test_security_headers(self, response, url: str) -> Optional[Dict]:
        """Test for missing security headers"""
        security_headers = {
            'Strict-Transport-Security': 'Missing HSTS header',
            'X-Frame-Options': 'Missing clickjacking protection',
            'X-Content-Type-Options': 'Missing MIME-type sniffing protection',
            'Content-Security-Policy': 'Missing CSP header',
            'X-XSS-Protection': 'Missing XSS protection header'
        }
        
        missing_headers = []
        for header, description in security_headers.items():
            if header not in response.headers:
                missing_headers.append(description)
                
        if missing_headers:
            return {
                'type': 'Missing Security Headers',
                'url': url,
                'severity': 'Medium',
                'description': 'One or more security headers are missing',
                'evidence': '\n'.join(missing_headers),
                'remediation': 'Implement recommended security headers'
            }
        return None

    def scan_endpoint(self, response, url: str) -> List[Dict]:
        """Perform all security checks on an endpoint"""
        findings = []
        
        # Run all security checks
        checks = [
            self.test_csrf,
            self.test_xss,
            self.test_information_disclosure,
            self.test_security_headers
        ]
        
        for check in checks:
            result = check(response, url)
            if result:
                findings.append(result)
                
        return findings
