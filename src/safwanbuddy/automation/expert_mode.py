import time
import threading
import json
import os
import re
from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.core.logging import logger

class TaskPlanner:
    def __init__(self):
        self.is_running = False
        self._current_task_thread = None
        self.history_file = os.path.join(os.getcwd(), "config", "expert_history.json")
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

    def plan_and_execute(self, goal: str):
        if self.is_running:
            logger.warning("Expert mode already running a task.")
            return

        steps = self._decompose_goal(goal)
        if not steps:
            logger.error(f"Could not decompose goal: {goal}")
            event_bus.emit("action_result", {"success": False, "message": "Goal unknown"})
            return

        self.is_running = True
        self._current_task_thread = threading.Thread(target=self._execute_steps, args=(goal, steps))
        self._current_task_thread.start()

    def _decompose_goal(self, goal: str):
        goal = goal.lower()
        
        # Advanced keyword weighting and regex-based decomposition
        # Pattern: research and broadcast/report/message about [topic]
        match = re.search(r"research (?:and|then) (?:report|broadcast|message) (?:about|on) (.+)", goal)
        if match:
            topic = match.group(1).strip()
            return [
                {"type": "web_request", "data": {"action": "search", "query": topic}},
                {"type": "expert_event", "data": {"status": "Researching topic..."}},
                {"type": "wait", "data": 4},
                {"type": "document_request", "data": {"action": "generate_summary", "topic": topic}},
                {"type": "expert_event", "data": {"status": "Generating summary..."}},
                {"type": "wait", "data": 3},
                {"type": "social_request", "data": {"action": "broadcast", "content": f"New research on {topic} is ready."}}
            ]

        # Pattern: setup profile [name]
        match = re.search(r"setup profile (.+)", goal)
        if match:
            name = match.group(1).strip()
            return [
                {"type": "automation_request", "data": {"action": "open_browser"}},
                {"type": "expert_event", "data": {"status": f"Setting up profile for {name}"}},
                {"type": "automation_request", "data": {"action": "type", "text": name}},
                {"type": "wait", "data": 2}
            ]

        # Multi-domain chain: web -> doc -> social
        if "market research" in goal:
            return [
                {"type": "web_request", "data": {"action": "market_analysis"}},
                {"type": "expert_event", "data": {"status": "Analyzing market trends"}},
                {"type": "wait", "data": 5},
                {"type": "document_request", "data": {"action": "create_excel", "name": "Market_Data"}},
                {"type": "social_request", "data": {"action": "post", "platform": "twitter", "text": "Market analysis completed."}}
            ]

        # Fallback split
        if " and " in goal or " then " in goal:
            parts = re.split(r" and | then ", goal)
            steps = []
            for part in parts:
                steps.append({"type": "voice_command", "data": part.strip()})
                steps.append({"type": "wait", "data": 2})
            return steps

        return None

    def _execute_steps(self, goal, steps):
        logger.info(f"Expert Mode starting: {goal}")
        event_bus.emit("system_state", "processing_expert")
        event_bus.emit("expert_event", {"status": "Initializing autonomous sequence...", "goal": goal})
        
        executed_steps = []
        try:
            for i, step in enumerate(steps):
                if not self.is_running: break
                
                if step["type"] == "wait":
                    time.sleep(step["data"])
                    continue
                
                logger.info(f"Expert Mode Step {i+1}/{len(steps)}: {step['type']}")
                event_bus.emit(step["type"], step["data"])
                
                executed_steps.append({"step": step, "timestamp": time.time(), "status": "success"})
                time.sleep(2)
            
            event_bus.emit("action_result", {"success": True, "message": "Autonomous task completed successfully."})
            self._log_history(goal, executed_steps, "completed")
            
        except Exception as e:
            logger.error(f"Expert Mode failed at step {len(executed_steps)}: {e}")
            self._log_history(goal, executed_steps, f"failed: {str(e)}")
            event_bus.emit("action_result", {"success": False, "error": str(e)})
        finally:
            self.is_running = False
            event_bus.emit("system_state", "idle")

    def _log_history(self, goal, steps, status):
        history_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "goal": goal,
            "status": status,
            "steps_count": len(steps)
        }
        
        data = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
            except:
                data = []
        
        data.append(history_entry)
        # Keep only last 50 entries
        data = data[-50:]
        
        with open(self.history_file, 'w') as f:
            json.dump(data, f, indent=4)

expert_mode_engine = TaskPlanner()
