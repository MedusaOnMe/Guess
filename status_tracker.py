import json
import time
from datetime import datetime

STATUS_FILE = "agent_status.json"

def update_status(step, message, progress=None, data=None):
    """Update the agent's current status for the dashboard"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "step": step,
        "message": message,
        "progress": progress,
        "data": data or {}
    }
    
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"[STATUS] {step}: {message}")

def get_status():
    """Get current agent status"""
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"step": "idle", "message": "Waiting for requests...", "progress": 0}

def update_thinking_status(message):
    """Update status to show the AI is thinking/analyzing"""
    update_status("thinking", f"🤔 {message}", progress=None)
    time.sleep(0.5)  # Brief pause for dramatic effect

def update_progress_status(step, total, message):
    """Update status with progress bar"""
    progress = (step / total) * 100
    update_status("processing", message, progress=progress)