# auth.py

from dataclasses import dataclass
from typing import Dict, Optional
import requests
import logging
import jwt
from bs4 import BeautifulSoup
from urllib.parse import urljoin

@dataclass
class AuthenticationConfig:
    """Authentication configuration"""
    auth_type: str  # basic, form, jwt, oauth
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    login_url: Optional[str] = None
    token_url: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

class AuthenticationManager:
    """Handles different authentication methods"""
    
    def __init__(self, config: AuthenticationConfig):
        self.config = config
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self.auth_tokens = {}
        
    def authenticate(self) -> Dict:
        """Perform authentication based on configured method"""
        try:
            if self.config.auth_type == 'basic':
                return self._basic_auth()
            elif self.config.auth_type == 'form':
                return self._form_auth()
            elif self.config.auth_type == 'jwt':
                return self._jwt_auth()
            elif self.config.auth_type == 'oauth':
                return self._oauth_auth()
            else:
                raise ValueError(f"Unsupported authentication type: {self.config.auth_type}")
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise
            
    def _basic_auth(self) -> Dict:
        """Perform basic authentication"""
        if not all([self.config.username, self.config.password]):
            raise ValueError("Username and password required for basic auth")
            
        self.session.auth = (self.config.username, self.config.password)
        return {'type': 'basic'}
        
    def _form_auth(self) -> Dict:
        """Perform form-based authentication"""
        if not self.config.login_url:
            raise ValueError("Login URL required for form auth")
            
        # Get login form and extract CSRF token if present
        response = self.session.get(self.config.login_url)
        csrf_token = self._extract_csrf_token(response)
        
        # Prepare login data
        login_data = {
            'username': self.config.username,
            'password': self.config.password
        }
        if csrf_token:
            login_data['csrf_token'] = csrf_token
            
        # Perform login
        response = self.session.post(
            self.config.login_url,
            data=login_data,
            allow_redirects=True
        )
        
        if response.status_code != 200:
            raise Exception(f"Form authentication failed: {response.status_code}")
            
        return {'type': 'form', 'cookies': dict(self.session.cookies)}