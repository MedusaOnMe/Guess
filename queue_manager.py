import json
import os
import time
from collections import deque
print("[QUEUE] Queue manager initialized - using file-based storage")

QUEUE_FILE = "queue.json"
RESULTS_FILE = "results_data.json"

def _load_queue():
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, 'r') as f:
                data = json.load(f)
                return deque(data)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return deque()

def _save_queue(queue_data):
    with open(QUEUE_FILE, 'w') as f:
        json.dump(list(queue_data), f)

def _load_results():
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return []

def _save_results(results_data):
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results_data, f)

def add_to_queue(user, place):
    print(f"[QUEUE] Adding to queue: {user} -> {place}")
    queue = _load_queue()
    queue.append({"user": user, "place": place, "status": "waiting", "result": None})
    _save_queue(queue)
    print(f"[QUEUE] Queue size now: {len(queue)}")
    print(f"[QUEUE] Saved to file: {QUEUE_FILE}")

def get_next():
    print(f"[QUEUE] get_next called, loading from file...")
    queue = _load_queue()
    print(f"[QUEUE] Queue length: {len(queue)}")
    
    # Check if any task is currently processing
    for task in queue:
        if task['status'] == 'processing':
            print(f"[QUEUE] Task already processing: {task['place']} - blocking new tasks")
            return None
    
    # Get next waiting task
    if queue and queue[0]['status'] == 'waiting':
        print(f"[QUEUE] Getting next task: {queue[0]}")
        queue[0]['status'] = 'processing'
        _save_queue(queue)
        return queue[0]
    print(f"[QUEUE] No waiting tasks found")
    return None

def complete_task(result):
    print(f"[QUEUE] Completing task with result: {result}")
    queue = _load_queue()
    results = _load_results()
    
    if queue:
        task = queue.popleft()
        task['status'] = 'done'
        task['result'] = result
        results.append(result)
        
        _save_queue(queue)
        _save_results(results)
        print(f"[QUEUE] Task completed. Results count: {len(results)}")
        return task
    else:
        print(f"[QUEUE] Warning: No tasks in queue to complete")
        return None

def get_results():
    results = _load_results()
    return results[-10:]

def get_stats():
    results = _load_results()
    if not results:
        return 0, 0, 0, 0
    scores = [r['score'] for r in results if 'score' in r]
    if not scores:
        return 0, 0, 0, 0
    return sum(scores), max(scores), min(scores), scores[-1]
