from typing import List, Dict, Union
from src.reporting.template_manager import ReportTemplateManager
import json
import datetime

class ReportGenerator:
    def __init__(self, template_manager: ReportTemplateManager):
        self.template_manager = template_manager
        
    def generate_report(self, scan_results: Dict) -> str:
        """Generate vulnerability report"""
        # Format scan duration to be more readable
        scan_duration = scan_results.get('scan_duration', '')
        if scan_duration:
            # Remove microseconds and just keep seconds
            scan_duration = scan_duration.split('.')[0] + 's'
            
        report_data = {
            'scan_date': datetime.datetime.now(),
            'target': scan_results.get('target', ''),
            'total_findings': len(scan_results.get('findings', [])),
            'findings': scan_results.get('findings', []),
            'modules': scan_results.get('modules', {}),
            'severity_counts': self._count_severities(scan_results.get('findings', [])),
            # Add scan metrics
            'total_urls_scanned': scan_results.get('total_urls_scanned', 0),
            'scan_duration': scan_duration,
            'total_tests_run': scan_results.get('total_tests_run', 0),
            'test_categories': scan_results.get('test_categories', {})
        }
        
        return self.template_manager.render_report('technical_details.html', report_data)
            
    def _count_severities(self, findings: List[Dict]) -> Dict[str, int]:
        """Count vulnerabilities by severity"""
        counts = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'Info': 0
        }
        
        for finding in findings:
            if isinstance(finding, dict) and 'severity' in finding:
                severity = finding['severity']
                if severity in counts:
                    counts[severity] += 1
                    
        return counts 