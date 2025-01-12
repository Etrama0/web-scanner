from typing import Dict, Optional
import requests
import logging
import jwt
import base64
from urllib.parse import urlparse
import json
from dataclasses import dataclass
from bs4 import BeautifulSoup

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
    auth_headers: Optional[Dict] = None

class AuthenticationManager:
    """Handle different authentication methods"""
    
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
        """Handle Basic Authentication"""
        if not self.config.username or not self.config.password:
            raise ValueError("Username and password required for basic auth")
            
        auth_string = base64.b64encode(
            f"{self.config.username}:{self.config.password}".encode()
        ).decode()
        
        return {
            'Authorization': f'Basic {auth_string}'
        }

    def _form_auth(self) -> Dict:
        """Handle Form-based Authentication"""
        if not self.config.login_url:
            raise ValueError("Login URL required for form auth")
            
        # First request to get CSRF token if present
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
            raise Exception("Form authentication failed")
            
        return dict(self.session.cookies)

    def _jwt_auth(self) -> Dict:
        """Handle JWT Authentication"""
        if self.config.token:
            # Validate JWT token
            try:
                jwt.decode(
                    self.config.token,
                    options={"verify_signature": False}
                )
                return {'Authorization': f'Bearer {self.config.token}'}
            except jwt.InvalidTokenError:
                self.logger.error("Invalid JWT token")
                raise
        elif self.config.token_url:
            # Request new JWT token
            data = {
                'username': self.config.username,
                'password': self.config.password
            }
            response = requests.post(self.config.token_url, json=data)
            if response.status_code == 200:
                token = response.json().get('token')
                return {'Authorization': f'Bearer {token}'}
            else:
                raise Exception("Failed to obtain JWT token")
        else:
            raise ValueError("Either token or token_url must be provided for JWT auth")

    def _oauth_auth(self) -> Dict:
        """Handle OAuth2 Authentication"""
        if not all([self.config.client_id, self.config.client_secret, self.config.token_url]):
            raise ValueError("client_id, client_secret, and token_url required for OAuth")
            
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret
        }
        
        response = requests.post(self.config.token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            return {
                'Authorization': f'Bearer {token_data["access_token"]}'
            }
        else:
            raise Exception("OAuth authentication failed")

    def _extract_csrf_token(self, response) -> Optional[str]:
        """Extract CSRF token from response"""
        # Try common CSRF token patterns
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check meta tags
        csrf_meta = soup.find('meta', {'name': ['csrf-token', '_csrf_token']})
        if csrf_meta:
            return csrf_meta.get('content')
            
        # Check form inputs
        csrf_input = soup.find('input', {'name': ['csrf_token', '_csrf_token']})
        if csrf_input:
            return csrf_input.get('value')
            
        return None

    def refresh_token(self) -> None:
        """Refresh authentication token if needed"""
        if self.config.auth_type in ['jwt', 'oauth']:
            self.auth_tokens = self.authenticate()
