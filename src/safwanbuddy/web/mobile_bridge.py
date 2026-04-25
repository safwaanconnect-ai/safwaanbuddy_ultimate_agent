from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.core.logging import logger
import os

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# Simple token for basic security
AUTH_TOKEN = "safwan_buddy_secret_2024"

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Auth-Token')
        if not token or token != AUTH_TOKEN:
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@app.route('/')
def index():
    return render_template('mobile_ui.html')

@app.route('/api/status', methods=['GET'])
@token_required
def get_status():
    return jsonify({
        "status": "online",
        "version": "7.0 Mobile Lite",
        "platform": "Windows (Bridge)"
    })

@app.route('/api/command', methods=['POST'])
@token_required
def post_command():
    data = request.json
    command = data.get('command')
    args = data.get('args', {})
    
    if not command:
        return jsonify({"error": "No command provided"}), 400
    
    logger.info(f"Mobile Bridge received command: {command} with args: {args}")
    
    # Emit event through the event bus, marking source as mobile
    event_bus.emit(command, {**args, "source": "mobile_bridge"})
    
    return jsonify({"status": "success", "message": f"Command {command} dispatched."})

@app.route('/api/logs', methods=['GET'])
@token_required
def get_logs():
    # In a real scenario, we'd pull from a log buffer
    return jsonify({
        "logs": ["Bridge connection established.", "Waiting for commands..."]
    })

def start_bridge(host='0.0.0.0', port=5000):
    logger.info(f"Starting Mobile Lite Bridge on {host}:{port}")
    # Running Flask in a separate thread
    flask_thread = threading.Thread(target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False), daemon=True)
    flask_thread.start()
