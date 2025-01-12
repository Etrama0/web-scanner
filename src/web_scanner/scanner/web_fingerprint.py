import requests
from bs4 import BeautifulSoup
import re
import hashlib
import logging
from urllib.parse import urljoin

class WebFingerprinter:
    """Web application fingerprinting module"""
    
    def __init__(self, target_url, timeout=10):
        self.target_url = target_url if target_url.startswith('http') else f'http://{target_url}'
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.findings = {
            'server': None,
            'technologies': [],
            'frameworks': [],
            'cms': None,
            'javascript_libs': [],
            'headers': {},
            'forms': [],
            'endpoints': set()
        }
        
        # Common technology signatures
        self.TECH_SIGNATURES = {
            'WordPress': [
                '/wp-content/',
                '/wp-includes/',
                'wp-json',
                'wp-login.php'
            ],
            'Drupal': [
                'Drupal.settings',
                '/sites/default/',
                'drupal.js'
            ],
            'Django': [
                'csrfmiddlewaretoken',
                '__admin__',
                'django-debug-toolbar'
            ],
            'Flask': [
                'Werkzeug',
                'flask.pocoo.org'
            ],
            'Laravel': [
                'laravel_session',
                '/vendor/laravel/',
                'Laravel'
            ]
        }

    def _make_request(self, url, method='GET', data=None):
        """Make HTTP request with error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; SecurityScanner/1.0)'
            }
            response = requests.request(method, url, headers=headers, 
                                     timeout=self.timeout, data=data,
                                     verify=False, allow_redirects=True)
            return response
        except Exception as e:
            self.logger.error(f"Request error for {url}: {str(e)}")
            return None

    def fingerprint_server(self):
        """Analyze server headers and basic technology stack"""
        response = self._make_request(self.target_url)
        if not response:
            return
            
        # Analyze headers
        self.findings['headers'] = dict(response.headers)
        self.findings['server'] = response.headers.get('Server')
        
        # Look for common technology indicators in headers
        for header, value in response.headers.items():
            if 'x-powered-by' in header.lower():
                self.findings['technologies'].append(value)
                
        return response

    def analyze_html(self, response):
        """Analyze HTML content for technology fingerprints"""
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check meta tags
            for meta in soup.find_all('meta'):
                if meta.get('name') == 'generator':
                    self.findings['cms'] = meta.get('content')
                    
            # Find JavaScript libraries
            for script in soup.find_all('script', src=True):
                src = script['src']
                for lib in ['jquery', 'angular', 'react', 'vue']:
                    if lib in src.lower():
                        self.findings['javascript_libs'].append(lib)
                        
            # Analyze forms
            for form in soup.find_all('form'):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'inputs': []
                }
                
                for input_field in form.find_all('input'):
                    form_data['inputs'].append({
                        'name': input_field.get('name'),
                        'type': input_field.get('type'),
                        'id': input_field.get('id')
                    })
                    
                self.findings['forms'].append(form_data)
                
        except Exception as e:
            self.logger.error(f"HTML analysis error: {str(e)}")

    def crawl_endpoints(self, max_depth=2):
        """Basic crawler to discover endpoints"""
        visited = set()
        to_visit = {self.target_url}
        depth = 0
        
        while to_visit and depth < max_depth:
            current_url = to_visit.pop()
            if current_url in visited:
                continue
                
            response = self._make_request(current_url)
            if not response:
                continue
                
            visited.add(current_url)
            self.findings['endpoints'].add(current_url)
            
            # Parse links from response
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)
                    if full_url.startswith(self.target_url):
                        to_visit.add(full_url)
            except Exception as e:
                self.logger.error(f"Crawling error: {str(e)}")
                
            depth += 1

    def fingerprint(self):
        """Perform complete fingerprinting"""
        response = self.fingerprint_server()
        if response:
            self.analyze_html(response)
            self.crawl_endpoints()
            
        return self.findings
