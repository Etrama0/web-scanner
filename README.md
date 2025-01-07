# Web Security Scanner

A comprehensive web application security scanner with advanced vulnerability detection capabilities and a modern web interface.

## Features

### Security Tests
- **Authentication Tests**
  - CSRF Protection Analysis
  - Session Management Verification
  - Password Policy Assessment
  - Authentication Bypass Testing

- **Injection Tests**
  - SQL Injection Detection
  - Cross-Site Scripting (XSS)
  - Command Injection
  - XML External Entity (XXE)

- **Configuration Tests**
  - Security Headers Analysis
  - SSL/TLS Configuration Check
  - Server Information Disclosure
  - Error Handling Assessment

- **Information Disclosure Tests**
  - Sensitive Data Exposure Check
  - Directory Listing Detection
  - File Inclusion Vulnerability Scan
  - Version Information Detection

### Advanced Features
- Modern Web Interface
- Real-time Scan Progress
- Detailed Vulnerability Reports
- Configurable Scan Options
- Multi-threaded Scanning
- Customizable Scan Depth

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/websecurity-scanner.git
cd websecurity-scanner
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package:
```bash
python setup.py install
```

## Usage

### Web Interface

1. Start the web server:
```bash
python -m src.ui.app
```

2. Open your browser and navigate to `http://localhost:5000`

3. Enter the target URL and configure scan options:
   - Target URL: The website to scan
   - Scan Type: Quick, Standard, Deep, or Custom
   - Threads: Number of concurrent scans (1-10)
   - Scan Depth: How deep to crawl (1-10)

4. Click "Start Scan" and monitor the progress

### Command Line

Basic scan:
```bash
webscan --target https://example.com --config src/config/scanner_config.yaml
```

Advanced options:
```bash
webscan --target https://example.com --config src/config/scanner_config.yaml --verbose
```

Available arguments:
```bash
webscan --help

Options:
  -h, --help         Show this help message and exit
  --config CONFIG    Path to configuration file (required)
  --target TARGET    Target URL to scan (required)
  --verbose         Enable verbose output
```

Example configuration file (`src/config/scanner_config.yaml`):
```yaml
scanner:
  threads: 5
  depth: 3
  timeout: 30
  user_agent: "WebSecurityScanner/1.0"
  verify_ssl: false
```

## Configuration

The scanner can be configured through:

1. Web Interface:
   - Adjust scan parameters in the UI
   - Select different scan types
   - Configure thread count and depth

2. Configuration File (`src/config/scanner_config.yaml`):
   - Set default values for timeouts, threads, etc.
   - Configure custom test patterns
   - Define scan behavior and limits

Example configuration options:
```yaml
scanner:
  # General settings
  threads: 5              # Number of concurrent threads
  depth: 3               # Maximum crawl depth
  timeout: 30            # Request timeout in seconds
  verify_ssl: false      # SSL verification
  
  # Scan settings
  max_urls: 100          # Maximum URLs to scan
  exclude_urls: []       # URLs to exclude
  allowed_domains: []    # Domains to include in scan
  
  # Test settings
  test_categories:       # Enable/disable test categories
    authentication: true
    injection: true
    configuration: true
    information: true
```

## Security Considerations

- Always obtain proper authorization before scanning any website
- Be cautious with aggressive scanning options
- Respect rate limits and robots.txt
- Use the tool responsibly and ethically

## Development

1. Set up development environment:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest tests/
```

3. Check code style:
```bash
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Disclaimer

This tool is for educational and ethical testing purposes only. Users are responsible for obtaining proper authorization before scanning any systems they don't own.