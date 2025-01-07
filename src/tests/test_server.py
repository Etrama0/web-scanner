from flask import Flask, request, render_template_string
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Test Server</h1>'

@app.route('/vulnerable')
def vulnerable():
    param = request.args.get('input', '')
    return f'<div>{param}</div>'

def run_test_server():
    app.run(port=5000)

def start_test_server():
    server_thread = threading.Thread(target=run_test_server)
    server_thread.daemon = True
    server_thread.start()
    return server_thread

if __name__ == '__main__':
    start_test_server() 