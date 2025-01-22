import logging
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import requests
from urllib.parse import urljoin, urlparse
import os
from dotenv import load_dotenv
from secrets import token_hex, token_urlsafe
import time
import hmac

class AdvancedVulnerabilityScanner:
    """Advanced vulnerability scanning module"""
    
    def __init__(self, config: Dict = None, logger=None):
        load_dotenv()
        self.api_key = os.getenv('SCANNER_API_KEY')
        self.test_credentials = {
            'username': os.getenv('TEST_USERNAME'),
            'password': os.getenv('TEST_PASSWORD')
        }
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.findings: List[Dict] = []
        
        self.patterns = self.load_patterns()
        self.csrf_token_pattern = re.compile(
            r'(?i)(csrf[-_]?token|authenticity[-_]?token|xsrf[-_]?token|_token)'
        )
        self.session_secret = os.getenv('SESSION_SECRET', token_hex(32))
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour default
        self.session_tokens = {}

    def load_patterns(self):
        # Load patterns from a secure source or configuration file
        return {
            'sql_injection': self.load_sql_injection_patterns(),
            'xss': self.load_xss_patterns(),
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

    def load_sql_injection_patterns(self):
        # Implement loading logic
        return []

    def load_xss_patterns(self):
        # Implement loading logic
        return []

    def generate_csrf_token(self) -> str:
        """Generate a secure CSRF token"""
        return token_hex(32)
        
    def validate_csrf_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token with session binding"""
        try:
            if not token or not session_id:
                return False
                
            # Add session binding to prevent token reuse
            expected_token = self.session_tokens.get(session_id)
            if not expected_token:
                return False
                
            # Use constant time comparison
            return hmac.compare_digest(token.encode(), expected_token.encode())
        except Exception as e:
            self.logger.error("CSRF validation failed",
                error=str(e),
                session_id=session_id
            )
            return False

    def create_session(self, user_id: str) -> Tuple[str, str]:
        """Create a new session with CSRF protection"""
        try:
            session_id = token_urlsafe(32)
            csrf_token = self.generate_csrf_token()
            
            session_data = {
                'user_id': user_id,
                'csrf_token': csrf_token,
                'created_at': time.time(),
                'expires_at': time.time() + self.session_timeout
            }
            
            # Store session data securely
            self.session_tokens[session_id] = session_data
            
            return session_id, csrf_token
            
        except Exception as e:
            self.logger.error("Session creation failed",
                error=str(e),
                user_id=user_id
            )
            raise

    def validate_session(self, session_id: str) -> bool:
        """Validate session with expiration check"""
        try:
            if not session_id:
                return False
                
            session_data = self.session_tokens.get(session_id)
            if not session_data:
                return False
                
            # Check session expiration
            if time.time() > session_data['expires_at']:
                del self.session_tokens[session_id]
                return False
                
            return True
            
        except Exception as e:
            self.logger.error("Session validation failed",
                error=str(e),
                session_id=session_id
            )
            return False

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
        # Part of configuration and security header analysis
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

    async def scan_endpoint(self, response, url: str) -> List[Dict]:
        try:
            if not self._validate_url(url):
                raise ValueError("Invalid URL format")
                
            findings = []
            for check in self._get_relevant_checks(response):
                try:
                    result = await check(response, url)
                    if result:
                        findings.append(result)
                except Exception as e:
                    self.logger.error(f"Check {check.__name__} failed: {str(e)}")
                    continue
            return findings
            
        except Exception as e:
            self.logger.error(f"Scan failed for {url}: {str(e)}")
            return []

    def _determine_endpoint_type(self, response) -> str:
        """Determine type of endpoint based on response"""
        # Part of reconnaissance and technology stack detection
        content_type = response.headers.get('Content-Type', '')
        if 'html' in content_type:
            return 'web_page'
        elif 'json' in content_type:
            return 'api'
        elif 'xml' in content_type:
            return 'xml'
        return 'unknown'

    def _get_relevant_checks(self, endpoint_type: str) -> List:
        """Get relevant security checks based on endpoint type"""
        common_checks = [self.test_security_headers]
        
        type_specific_checks = {
            'web_page': [self.test_csrf, self.test_xss],
            'api': [self.test_information_disclosure],
            'xml': [self.test_xxe],
            'unknown': []
        }
        
        return common_checks + type_specific_checks.get(endpoint_type, [])

    def _validate_finding(self, finding: Dict) -> bool:
        """Validate finding to prevent false positives"""
        required_fields = ['type', 'url', 'severity', 'description']
        if not all(field in finding for field in required_fields):
            return False
            
        # Validate severity level
        if finding['severity'] not in ['High', 'Medium', 'Low', 'Info']:
            return False
            
        return True
