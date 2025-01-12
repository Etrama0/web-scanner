from jinja2 import Environment, FileSystemLoader
import os
from typing import Dict, Any
import json
import yaml
from datetime import datetime

class ReportTemplateManager:
    """Manage custom report templates"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
        # Register custom filters
        self.env.filters['severity_color'] = self._severity_color
        self.env.filters['format_datetime'] = self._format_datetime
        
    def render_report(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render report using specified template"""
        template = self.env.get_template(template_name)
        return template.render(**data)
        
    def _severity_color(self, severity: str) -> str:
        """Convert severity to color code"""
        colors = {
            'Critical': '#FF0000',
            'High': '#FF4500',
            'Medium': '#FFA500',
            'Low': '#FFD700',
            'Info': '#00FF00'
        }
        return colors.get(severity, '#808080')
        
    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime for reports"""
        return dt.strftime('%Y-%m-%d %H:%M:%S')
