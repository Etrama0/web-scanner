from flask import Flask, jsonify, request, render_template
import logging
import asyncio
from datetime import datetime
from ..config.scanner_config import load_scanner_config
from ..scanner.vulnerability_scanner import VulnerabilityScanner

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Track active scans
active_scans = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            app.logger.error("No URL provided in request")
            return "Scan Error: No URL Provided", 400
        
        url = data['url']
        app.logger.info(f"Scanning URL: {url}")
        # Proceed with scan logic
        return jsonify({"status": "success", "message": f"Scanning {url}"})
    
    except Exception as e:
        app.logger.error(f"Error during scan: {str(e)}")
        return f"Scan Error: {str(e)}", 400

@app.route('/api/scan', methods=['POST'])
async def start_scan():
    try:
        data = request.get_json()
        target_url = data.get('target_url')
        config_path = data.get('config_path', 'config/scanner_config.yaml')

        if not target_url:
            return jsonify({'error': 'Target URL is required'}), 400

        # Load and validate config
        try:
            config = load_scanner_config(config_path)
            config.target_url = target_url
        except Exception as e:
            app.logger.error(f"Config loading error: {str(e)}")
            return jsonify({'error': 'Invalid configuration'}), 400

        # Initialize scanner
        scanner = VulnerabilityScanner(config)
        
        # Generate scan ID
        scan_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Store scan info
        active_scans[scan_id] = {
            'status': 'running',
            'start_time': datetime.now(),
            'target': target_url,
            'results': None
        }

        # Run scan asynchronously
        asyncio.create_task(run_scan(scan_id, scanner))

        return jsonify({
            'scan_id': scan_id,
            'status': 'started',
            'message': 'Scan initiated successfully'
        })

    except Exception as e:
        app.logger.error(f"Scan error: {str(e)}")
        return jsonify({'error': str(e)}), 500

async def run_scan(scan_id: str, scanner: VulnerabilityScanner):
    """Run scan asynchronously and store results"""
    try:
        results = await scanner.scan()
        active_scans[scan_id].update({
            'status': 'completed',
            'results': results,
            'end_time': datetime.now()
        })
    except Exception as e:
        app.logger.error(f"Scan {scan_id} failed: {str(e)}")
        active_scans[scan_id].update({
            'status': 'failed',
            'error': str(e),
            'end_time': datetime.now()
        })

@app.route('/api/scan/<scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    """Get status and results of a specific scan"""
    scan_info = active_scans.get(scan_id)
    if not scan_info:
        return jsonify({'error': 'Scan not found'}), 404
    
    return jsonify(scan_info)

if __name__ == '__main__':
    app.run(debug=True)
