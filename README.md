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

#### Basic Usage
Run quick scans with minimal configuration:
```bash
webscan --url example.com
```

#### Advanced Usage
Execute comprehensive scans with multiple modules:
```bash
webscan --url example.com \
  --modules recon,exploit,brute \
  --output-dir ./reports \
  --verbose
```

#### Scan Report Formats

The scanner generates comprehensive security assessment reports in the following formats:

- **HTML** (default): Interactive report with detailed findings and remediation steps
- **JSON**: Machine-readable format for integration with other security tools

To specify the report format when running a scan:

```bash
# For HTML format.
webscan --url example.com

# For json format.
webscan --url example.com --format json
```


#### Module-Based Scanning
```bash
# Reconnaissance only
webscan --url example.com --modules recon

# Full security audit
webscan --url example.com --modules recon brute exploit
```

#### Using Custom Configurations
```bash
python -m web_scanner.main \
  --config config/scanner_config.yaml \
  --target example.com
```

#### Available Options
Required:
```bash
--url: Target URL/domain (e.g., example.com)
```
Command line options:
```bash
--url: Target URL/domain to scan (required)
--modules: Modules to run (recon,auth,injection,config)
--format: Output format (json|html, default: html)
--output-dir: Directory for scan reports (default: "reports")
--verbose: Enable verbose logging
--config: Path to custom configuration file
```

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
pip install -r requirements.txt
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

MIT License - See the LICENSE file for details.

## Disclaimer

Web Security Scanner is a cybersecurity tool designed to perform security assessments on specified targets. While it aims to identify vulnerabilities and enhance security, it may inadvertently cause malfunctions, crashes, or potential data loss on the target system.

Using a Web Security Scanner to attack or assess a target without the explicit consent of its owner is illegal. It is the end user's sole responsibility to comply with all applicable local laws and regulations.

The developer assumes no liability and is not responsible for any misuse, damage, or unintended consequences arising from the use of this program.

## Acknowledgment

This project, Web Security Scanner, was developed using AI-assisted tools. AI was utilized for code generation, optimization, and documentation enhancements to streamline the development process. The integration of AI support has been instrumental in accelerating the project's completion and ensuring high-quality outputs.

I appreciate the role of AI in enhancing productivity and welcome any feedback or suggestions for improvement.
