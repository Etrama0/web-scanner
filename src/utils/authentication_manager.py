from dataclasses import dataclass
import requests
import logging
from typing import Dict, Optional
import jwt
import base64
from bs4 import BeautifulSoup

@dataclass
class AuthConfig:
    auth_type: str  # basic, form, jwt, oauth
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    login_url: Optional[str] = None
    token_url: Optional[str] = None

class AuthenticationManager:
    def __init__(self, config: AuthConfig):
        self.config = config
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def authenticate(self) -> Dict:
        """Perform authentication based on configured method"""
        if self.config.auth_type == 'basic':
            return self._basic_auth()
        elif self.config.auth_type == 'form':
            return self._form_auth()
        elif self.config.auth_type == 'jwt':
            return self._jwt_auth()
        else:
            raise ValueError(f"Unsupported auth type: {self.config.auth_type}") 