import json
from datetime import datetime
from typing import Dict, List, Union, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def generate_report(
    scan_results: Union[Dict, List], 
    output_format: str = 'html',
    output_file: Optional[str] = None,
    template_path: Optional[str] = None
) -> str:
    """Generate a report from scan results"""
    if isinstance(scan_results, list):
        # Convert list of findings to proper report structure
        scan_data = {
            'findings': scan_results,
            'stats': {
                'total_findings': len(scan_results),
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(), 
                'duration': 0
            }
        }
    else:
        scan_data = scan_results

    test_name_map = {
        'headers': 'Security Headers',
        'ssl_tls': 'SSL/TLS Configuration',
        'server_info': 'Server Information',
        'version_info': 'Version Disclosure',
        'sensitive_data': 'Sensitive Data Exposure',
        'directory_listing': 'Directory Listing',
        'xss': 'Cross-Site Scripting',
        'sql': 'SQL Injection',
        'command': 'Command Injection',
        'csrf': 'CSRF Protection',
        'session': 'Session Management',
        'auth_bypass': 'Authentication Bypass',
        'rce': 'Remote Code Execution',
        'lfi': 'Local File Inclusion',
        'xxe': 'XML External Entity',
        'deserialization': 'Deserialization'
    }

    # Process scan data into template format
    template_data = {
        'target': scan_results.get('target', 'Unknown'),
        'timestamp': scan_results.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'urls_scanned': scan_results.get('urls_scanned', 1),
        
        # Calculate test statistics
        'total_tests': sum(m.get('tests_available', 0) for m in scan_results.get('modules', [])),
        'tests_completed': sum(m.get('tests_run', 0) for m in scan_results.get('modules', [])),
        'total_findings': len(scan_results.get('findings', [])),
        'scan_duration': f"{scan_results.get('duration', 0):.2f}s",
        
        # Module data
        'modules': [
            {
                'name': module.get('name', ''),
                'tests_available': module.get('tests_available', 0),
                'tests_run': module.get('tests_run', 0),
                'duration': f"{module.get('duration', 0):.2f}",
                'issues_found': len(module.get('findings', []))
            }
            for module in scan_results.get('modules', [])
        ],
        
        # Individual test data
        'tests': [
            {
                'name': test_name_map.get(test_name, test_name),
                'status': 'completed',
                'duration': f"{(mod['duration']/len(mod.get('test_names',[]))):.2f}s" 
                            if len(mod.get('test_names',[])) > 0 else "0.00s",
                'issues_found': sum(
                    1 for f in mod.get('findings', []) 
                    if test_name.lower() in f.get('type','').lower()
                )
            }
            for mod in scan_results.get('modules', [])
            for test_name in mod.get('test_names', [])
        ],
        
        # Findings
        'findings': scan_results.get('findings', [])
    }

    if output_format == 'json':
        return _generate_json_report(template_data, output_file)
    else:
        return _generate_html_report(template_data, output_file, template_path)

def _generate_json_report(report_data: Dict, output_file: Optional[str] = None) -> str:  
    """Generate JSON format report"""
    report_content = json.dumps(report_data, indent=2)
    if output_file:
        Path(output_file).write_text(report_content)
        return output_file
    return report_content

def _generate_html_report(
    report_data: Dict, 
    output_file: Optional[str] = None,
    template_path: Optional[str] = None
) -> str:
    """Generate HTML report using template"""
    # Get template directory path
    if template_path:
        template_dir = Path(template_path).parent
        template_file = Path(template_path).name
    else:
        template_dir = Path(__file__).parent / 'templates'
        template_file = 'technical_details.html'
        
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True
    )
    
    # Load and render template
    template = env.get_template(template_file)
    report_content = template.render(**report_data)
    
    if output_file:
        Path(output_file).write_text(report_content)
        return output_file
        
    return report_content

def _count_severities(findings: List[Dict]) -> Dict[str, int]:
    """Count findings by severity level"""
    counts = {}
    for finding in findings:
        severity = finding.get('severity', 'Unknown')
        counts[severity] = counts.get(severity, 0) + 1
    return counts
