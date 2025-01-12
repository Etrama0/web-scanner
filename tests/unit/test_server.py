from flask import Flask, request, render_template_string
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Test Server</h1>'

@app.route('/vulnerable')
def vulnerable():
    try:
        param = request.args.get('input', '')
        return f'<div>{param}</div>'
    except Exception as e:
        return f'Error: {str(e)}', 500

def run_test_server():
    try:
        app.run(port=5000)
    except Exception as e:
        print(f"Server error: {str(e)}")

def start_test_server():
    server_thread = threading.Thread(target=run_test_server)
    server_thread.daemon = True
    server_thread.start()
    return server_thread

if __name__ == '__main__':
    start_test_server()
