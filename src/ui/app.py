from flask import Flask, jsonify, request, render_template
import uuid
from src.scanner.vulnerability_scanner import VulnerabilityScanner
from src.config.scanner_config import ScannerConfig
import asyncio
from datetime import datetime
import time

app = Flask(__name__)
scans = {}

class ScanSession:
    def __init__(self, target):
        self.target = target
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.findings = []

    def start(self):
        self.start_time = datetime.now()

    def end(self):
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

async def run_scan_async(scan_id: str, target: str, scanner: VulnerabilityScanner):
    try:
        # Perform scan
        result = await scanner.scan(target)
        
        # Update scan information
        scans[scan_id]['status'] = 'completed'
        scans[scan_id]['findings'] = result.get('findings', [])
        scans[scan_id]['stats'] = {
            'urls_scanned': result.get('total_urls_scanned', 0),
            'tests_performed': result.get('total_tests_run', 0),
            'issues_found': len(result.get('findings', [])),
            'duration': result.get('scan_duration', '00:00'),
            'test_categories': result.get('test_categories', {})
        }
        
    except Exception as e:
        scans[scan_id]['status'] = 'failed'
        scans[scan_id]['error'] = str(e)

def run_scan(scan_id: str, target: str):
    try:
        scanner = scans[scan_id]['scanner']
        
        # Create event loop in the new thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async scan
        loop.run_until_complete(run_scan_async(scan_id, target, scanner))
        loop.close()
        
    except Exception as e:
        scans[scan_id]['status'] = 'failed'
        scans[scan_id]['error'] = str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def start_scan():
    try:
        data = request.json
        target = data.get('target')
        options = data.get('options', {})
        
        # Initialize scanner with config
        config = ScannerConfig(
            threads=options.get('threads', 2),
            max_crawl_depth=options.get('depth', 3),
            timeout=options.get('timeout', 30)  # Increased timeout
        )
        
        scanner = VulnerabilityScanner(config)
        
        # Run scan synchronously for now to ensure proper results
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scanner.scan(target))
        loop.close()
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/scan/status/<scan_id>')
def get_scan_status(scan_id):
    if scan_id not in scans:
        return jsonify({
            'status': 'error',
            'error': 'Scan not found'
        }), 404
        
    scan = scans[scan_id]
    return jsonify({
        'status': scan['status'],
        'findings': scan['findings'] if scan['status'] == 'completed' else [],
        'stats': scan.get('stats', {})
    })

if __name__ == '__main__':
    app.run(debug=True) 