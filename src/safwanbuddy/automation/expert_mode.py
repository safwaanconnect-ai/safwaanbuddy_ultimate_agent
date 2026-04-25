import time
import threading
from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.core.logging import logger

class TaskPlanner:
    def __init__(self):
        self.is_running = False
        self._current_task_thread = None

    def plan_and_execute(self, goal: str):
        """
        Decomposes high-level goal into a sequence of events.
        """
        if self.is_running:
            logger.warning("Expert mode already running a task.")
            return

        steps = self._decompose_goal(goal)
        if not steps:
            logger.error(f"Could not decompose goal: {goal}")
            event_bus.emit("action_result", {"success": False, "message": "Goal unknown"})
            return

        self.is_running = True
        self._current_task_thread = threading.Thread(target=self._execute_steps, args=(steps,))
        self._current_task_thread.start()

    def _decompose_goal(self, goal: str):
        goal = goal.lower()
        # Predefined complex task chains
        if "research and report" in goal:
            product = goal.replace("research and report on", "").strip()
            return [
                {"type": "web_request", "data": {"action": "compare_price", "product": product}},
                {"type": "wait", "data": 5},
                {"type": "document_request", "data": {"action": "generate_report", "topic": product}},
                {"type": "social_request", "data": {"action": "message", "name": "Manager", "message": f"I've completed the research report on {product}."}}
            ]
        elif "prepare profile" in goal:
            return [
                {"type": "automation_request", "data": {"action": "open_browser"}},
                {"type": "wait", "data": 2},
                {"type": "automation_request", "data": {"action": "type_profile", "field": "full_name"}},
                {"type": "automation_request", "data": {"action": "type_profile", "field": "email"}}
            ]
        
        # Generic fallback for demo if it contains multiple keywords
        if "and" in goal:
            # Simple splitter logic for demonstration
            parts = goal.split("and")
            steps = []
            for part in parts:
                steps.append({"type": "voice_command", "data": part.strip()})
                steps.append({"type": "wait", "data": 3})
            return steps

        return None

    def _execute_steps(self, steps):
        logger.info("Starting Expert Mode execution chain.")
        event_bus.emit("system_state", "processing_expert")
        
        try:
            for step in steps:
                if step["type"] == "wait":
                    time.sleep(step["data"])
                    continue
                
                logger.info(f"Expert Mode executing: {step['type']} with {step['data']}")
                event_bus.emit(step["type"], step["data"])
                # Wait a bit between steps to allow systems to react
                time.sleep(3) 
            
            event_bus.emit("action_result", {"success": True, "message": "Expert task completed"})
        except Exception as e:
            logger.error(f"Expert Mode failed: {e}")
            event_bus.emit("action_result", {"success": False, "error": str(e)})
        finally:
            self.is_running = False
            event_bus.emit("system_state", "idle")

expert_mode_engine = TaskPlanner()
