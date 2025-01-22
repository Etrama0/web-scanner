import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from web_scanner.config.scanner_config import ScannerConfig
from web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
from web_scanner.reporting.template_manager import ReportTemplateManager
from web_scanner.reporting.report_generator import ReportGenerator
import os
import datetime

def main():
    # Load config
    config = ScannerConfig.from_yaml('src/config/scanner_config.yaml')
    
    # Initialize components
    scanner = VulnerabilityScanner(config)
    template_manager = ReportTemplateManager()
    report_generator = ReportGenerator(template_manager)
    
    # Run scan
    target = "http://example.com"
    results = scanner.scan(target)
    
    # Add scan validation
    validated_results = []
    seen_issues = set()
    
    for result in results:
        # Deduplicate similar findings
        result_hash = f"{result['type']}:{result['url']}:{result['severity']}"
        if result_hash in seen_issues:
            continue
        seen_issues.add(result_hash)
        
        # Validate confidence score
        if result.get('confidence_score', 0) < config.min_confidence_score:
            continue
            
        validated_results.append(result)
    
    # Generate report with validated results
    report = report_generator.generate_report(validated_results)
    
    # Save report
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    
    report_path = os.path.join(output_dir, f"scan_report_{datetime.datetime.now():%Y%m%d_%H%M%S}.html")
    with open(report_path, 'w') as f:
        f.write(report)
        
    print(f"Scan completed. Found {len(validated_results)} potential vulnerabilities.")
    print(f"Report saved to: {report_path}")

if __name__ == "__main__":
    main()
