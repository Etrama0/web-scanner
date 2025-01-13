# Web Security Scanner

An advanced web security assessment tool with real-time scanning capabilities and a modern web interface.

## Project Structure
```
web-scanner/
├── src/
│   └── web_scanner/
│       ├── config/          # Configuration management
│       ├── core/           # Core functionality
│       ├── scanner/        # Security scanning modules
│       ├── reporting/      # Report generation
│       └── ui/            # Web interface
├── tests/                  # Test suites
├── config/                # Default configurations
├── reports/               # Generated scan reports
└── logs/                  # Scan logs
```

## Features

### Core Functionality
- Modular scanning architecture
- Asynchronous scan execution
- Real-time progress monitoring
- HTML report generation
- Configurable scan parameters

### Security Tests
- Authentication Tests
  - CSRF Protection
  - Session Management
  - Password Policy Analysis
  - Auth Bypass Detection

- Web Vulnerabilities
  - SQL Injection
  - XSS (Cross-site Scripting)
  - Command Injection
  - Information Disclosure

- Configuration Analysis
  - Security Headers
  - SSL/TLS Configuration
  - Server Information Leaks
  - Error Handling Review

- Information Disclosure Tests
  - Sensitive Data Exposure Check
  - Directory Listing Detection
  - File Inclusion Vulnerability Scan
  - Version Information Detection

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Etrama0/webs-scanner.git
cd web-scanner
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install package in development mode:
```bash
pip install -e .
```

## Usage

### Command Line Interface

The scanner can be run using the following commands:

```bash
# Using the python module
python -m web_scanner.main --config config/scanner_config.yaml --target example.com

# Using the webscan command
webscan --url example.com --modules recon --format html --verbose

# Additional webscan options
webscan --url example.com \
  --modules recon,auth,injection \
  --format json \
  --output-dir reports \
  --verbose
```

Command line options:
- `--url`: Target URL/domain to scan (required)
- `--modules`: Modules to run (recon,auth,injection,config)
- `--format`: Output format (json|html, default: html)
- `--output-dir`: Directory for scan reports (default: "reports")
- `--verbose`: Enable verbose logging
- `--config`: Path to custom configuration file

[![TTutorial video.](https://img.youtube.com/vi/HDwWg5X10Gk/0.jpg)](https://www.youtube.com/watch?v=HDwWg5X10Gk)

Watch this silent tutorial to create detailed security assessment reports using the GitHub Web-Scanner project. Follow step-by-step as we navigate the scanning process and review the resulting HTML reports.

### Web Interface

1. Start the web server:
```bash
python -m web_scanner.ui.app
```

2. Access the interface at `http://localhost:5000`

3. Enter target URL and configure scan options:
   - Target URL: Website to scan
   - Scan options:
     - Thread count
     - Scan depth
     - Test categories

> ⚠️ **Note:** The web interface (`python -m web_scanner.ui.app`) is currently under development and not fully functional. Please use the command line interface instead.

### Example Usage

Using the provided example:
```python
from web_scanner.config.scanner_config import ScannerConfig
from web_scanner.scanner.vulnerability_scanner import VulnerabilityScanner

# Load config
config = ScannerConfig.from_yaml('config/scanner_config.yaml')

# Initialize scanner
scanner = VulnerabilityScanner(config)

# Run scan
target = "https://example.com"
results = scanner.scan(target)
```

### Configuration

Default configuration (`config/scanner_config.yaml`):
```yaml
scanner:
  threads: 5
  depth: 3
  timeout: 30
  user_agent: "WebSecurityScanner/1.0"
  verify_ssl: false

logging:
  level: INFO
  file: logs/scan_%Y%m%d_%H%M%S.log
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest tests/
```

3. Generate reports:
```python
from web_scanner.reporting.report_generator import ReportGenerator
from web_scanner.reporting.template_manager import ReportTemplateManager

template_manager = ReportTemplateManager()
report_generator = ReportGenerator(template_manager)
report = report_generator.generate_report(scan_results)
```

## API Endpoints

- `GET /` - Web interface
- `POST /scan` - Start new scan
  ```json
  {
    "url": "https://example.com",
    "options": {
      "threads": 5,
      "depth": 3
    }
  }
  ```
- `GET /api/scan/<scan_id>` - Get scan status/results

## Security Considerations

- Obtain proper authorization before scanning
- Respect rate limits and robots.txt
- Use responsibly and ethically
- Test thoroughly in isolated environments

## License

MIT License - See LICENSE file for details.

## Disclaimer

This tool is for educational and ethical testing purposes only. Always obtain proper authorization before scanning any systems.
