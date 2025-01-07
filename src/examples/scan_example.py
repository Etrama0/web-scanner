from src.config.scanner_config import ScannerConfig
from src.scanner.vulnerability_scanner import VulnerabilityScanner
from src.reporting.template_manager import ReportTemplateManager
from src.reporting.report_generator import ReportGenerator
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
    
    # Generate report
    report = report_generator.generate_report(results)
    
    # Save report
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    
    report_path = os.path.join(output_dir, f"scan_report_{datetime.datetime.now():%Y%m%d_%H%M%S}.html")
    with open(report_path, 'w') as f:
        f.write(report)
        
    print(f"Scan completed. Found {len(results)} potential vulnerabilities.")
    print(f"Report saved to: {report_path}")

if __name__ == "__main__":
    main() 