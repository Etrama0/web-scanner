#!/usr/bin/env python3

import argparse
import logging
from datetime import datetime
from pathlib import Path
from web_scanner.config.scanner_config import ScannerConfig
from web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner
from web_scanner.reporting.report_generator import ReportGenerator
from web_scanner.reporting.template_manager import ReportTemplateManager
import asyncio
import sys
import yaml

def setup_logging(verbose: bool, log_file: str = None):
    """Configure logging settings"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory if it doesn't exist
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="Web Security Scanner")
    parser.add_argument("--config", required=True, help="Path to config file")
    parser.add_argument("--target", required=True, help="Target URL or IP")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    # Setup logging
    log_file = f"logs/scan_{datetime.now():%Y%m%d_%H%M%S}.log"
    setup_logging(args.verbose, log_file)
    
    try:
        # Load config
        config = ScannerConfig.from_yaml(args.config)
        
        # Update target URL to use HTTPS
        target = args.target
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"
        
        # Initialize scanner
        scanner = VulnerabilityScanner(config)
        
        # Run scan
        results = asyncio.run(scanner.scan(target))
        
        # Generate report
        template_manager = ReportTemplateManager()
        report_generator = ReportGenerator(template_manager)
        report = report_generator.generate_report(results)
        
        # Save report
        output_dir = "reports"
        Path(output_dir).mkdir(exist_ok=True)
        report_path = Path(output_dir) / f"scan_report_{datetime.now():%Y%m%d_%H%M%S}.html"
        report_path.write_text(report)
        
        print(f"Scan completed. Report saved to: {report_path}")
        
    except FileNotFoundError as e:
        logging.error(f"Configuration file not found: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f"Invalid YAML configuration: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Scan failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
