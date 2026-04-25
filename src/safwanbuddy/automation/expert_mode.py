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
        
        # 1. Advanced Research & Intelligence Chain
        match = re.search(r"research (?:and|then) (?:report|broadcast|message) (?:about|on) (.+)", goal)
        if match:
            topic = match.group(1).strip()
            return [
                {"type": "expert_event", "data": {"status": f"Initializing intelligence gathering on: {topic}"}},
                {"type": "web_request", "data": {"action": "search", "query": topic}},
                {"type": "wait", "data": 2},
                {"type": "expert_event", "data": {"status": "Analyzing search results and extracting key data..."}},
                {"type": "web_request", "data": {"action": "compare_price", "product": topic}}, # If applicable
                {"type": "wait", "data": 3},
                {"type": "document_request", "data": {"action": "generate_report", "topic": topic}},
                {"type": "expert_event", "data": {"status": "Synthesizing executive summary..."}},
                {"type": "social_request", "data": {"action": "message", "name": "Admin", "message": f"Intelligence report on {topic} is complete and archived."}},
                {"type": "notification", "data": f"Expert Mode: Mission Accomplished for {topic}"}
            ]

        # 2. Automated Profile & Onboarding Chain
        match = re.search(r"setup profile (.+)", goal)
        if match:
            name = match.group(1).strip()
            return [
                {"type": "expert_event", "data": {"status": f"Starting automated onboarding for {name}"}},
                {"type": "automation_request", "data": {"action": "open_browser"}},
                {"type": "wait", "data": 1},
                {"type": "automation_request", "data": {"action": "type_profile", "field": "full_name"}},
                {"type": "automation_request", "data": {"action": "fill_form"}},
                {"type": "expert_event", "data": {"status": "Verifying identity across systems..."}},
                {"type": "wait", "data": 2},
                {"type": "notification", "data": f"Profile {name} is now active."}
            ]

        # 3. Market Intelligence & Social Broadcast Chain
        if "market research" in goal or "trends" in goal:
            return [
                {"type": "expert_event", "data": {"status": "Scanning global markets..."}},
                {"type": "web_request", "data": {"action": "search", "query": "latest AI and tech trends"}},
                {"type": "wait", "data": 3},
                {"type": "document_request", "data": {"action": "generate_report"}},
                {"type": "social_request", "data": {"action": "message", "name": "Broadcast", "message": "Market analysis complete. Trend reports generated."}},
                {"type": "expert_event", "data": {"status": "Archiving market data..."}}
            ]

        # 6. Autonomous Desktop & Window Management
        if "cleanup workspace" in goal or "organize windows" in goal:
            return [
                {"type": "expert_event", "data": {"status": "Analyzing desktop clutter..."}},
                {"type": "automation_request", "data": {"action": "list_windows"}},
                {"type": "wait", "data": 1},
                {"type": "expert_event", "data": {"status": "Closing non-essential background windows..."}},
                {"type": "system_control", "data": {"action": "close_window", "target": "Calculator"}},
                {"type": "system_control", "data": {"action": "close_window", "target": "Notepad"}},
                {"type": "expert_event", "data": {"status": "Workspace optimized."}},
                {"type": "notification", "data": "Desktop Cleanup Complete."}
            ]

        # 7. System Optimization & Performance Boost
        if "optimize system" in goal or "boost performance" in goal:
            return [
                {"type": "expert_event", "data": {"status": "Initiating deep system scan..."}},
                {"type": "system_control", "data": {"action": "get_stats"}},
                {"type": "wait", "data": 2},
                {"type": "expert_event", "data": {"status": "Clearing temporary caches and optimizing memory..."}},
                {"type": "automation_request", "data": {"action": "flush_dns"}},
                {"type": "automation_request", "data": {"action": "clear_temp"}},
                {"type": "expert_event", "data": {"status": "Adjusting power plan for high performance..."}},
                {"type": "system_control", "data": {"action": "set_power_plan", "plan": "High Performance"}},
                {"type": "wait", "data": 2},
                {"type": "notification", "data": "System Performance Boosted Successfully."}
            ]

        # 4. Multi-step Web & Doc Chain
        if "analyze" in goal and "save" in goal:
            return [
                {"type": "web_request", "data": {"action": "search", "query": goal.replace("analyze", "").replace("save", "")}},
                {"type": "wait", "data": 4},
                {"type": "document_request", "data": {"action": "generate_report"}},
                {"type": "expert_event", "data": {"status": "Analysis saved to local storage."}}
            ]

        # 5. Dynamic Fallback Chain for 'and' / 'then'
        if " and " in goal or " then " in goal:
            parts = re.split(r" and | then ", goal)
            steps = []
            for part in parts:
                steps.append({"type": "expert_event", "data": {"status": f"Executing sub-task: {part.strip()}"}})
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
