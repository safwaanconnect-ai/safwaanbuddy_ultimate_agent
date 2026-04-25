import json
import time
import threading
import keyboard
import mouse
from src.safwanbuddy.core import logger, event_bus

class WorkflowEngine:
    def __init__(self):
        self.workflows = {}
        self.is_recording = False
        self.recorded_steps = []
        self._last_event_time = 0

    def start_recording(self):
        self.is_recording = True
        self.recorded_steps = []
        self._last_event_time = time.time()
        logger.info("Started recording workflow.")
        event_bus.emit("system_log", "Recording started...")
        
        # Start hooks
        mouse.on_click(self._on_click)
        keyboard.on_press(self._on_key)

    def _on_click(self):
        if not self.is_recording:
            return
        x, y = mouse.get_position()
        self.add_step("click", x=x, y=y)

    def _on_key(self, event):
        if not self.is_recording:
            return
        if event.name == 'esc': # Stop recording on Esc
            event_bus.emit("automation_request", {"action": "stop_recording"})
            return
        self.add_step("key", key=event.name)

    def stop_recording(self, name: str):
        if not self.is_recording:
            return []
        self.is_recording = False
        
        # Stop hooks
        try:
            mouse.unhook_all()
            keyboard.unhook_all()
        except:
            pass
            
        self.workflows[name] = self.recorded_steps
        logger.info(f"Stopped recording workflow: {name}. Recorded {len(self.recorded_steps)} steps.")
        event_bus.emit("system_log", f"Recording stopped. {len(self.recorded_steps)} steps.")
        return self.recorded_steps

    def add_step(self, step_type: str, **kwargs):
        if self.is_recording:
            now = time.time()
            delay = now - self._last_event_time
            self._last_event_time = now
            
            step = {
                "type": step_type, 
                "delay": delay,
                **kwargs
            }
            self.recorded_steps.append(step)

    def save_workflow(self, name: str, steps: list, file_path: str):
        workflow = {"name": name, "steps": steps, "version": "1.0"}
        with open(file_path, 'w') as f:
            json.dump(workflow, f, indent=4)
        logger.info(f"Workflow {name} saved to {file_path}")

    def run_workflow(self, file_path: str):
        with open(file_path, 'r') as f:
            workflow = json.load(f)
        
        logger.info(f"Running workflow: {workflow['name']}")
        from src.safwanbuddy.automation.click_system import click_system
        from src.safwanbuddy.automation.type_system import type_system
        
        for step in workflow['steps']:
            time.sleep(step.get("delay", 0.5))
            
            step_type = step.get("type")
            if step_type == "click":
                x, y = step.get("x"), step.get("y")
                if x is not None and y is not None:
                    import pyautogui
                    pyautogui.click(x, y)
                elif step.get("target"):
                    click_system.click_text(step.get("target"))
            elif step_type == "key":
                import pyautogui
                pyautogui.press(step.get("key"))
            elif step_type == "type":
                type_system.type_text(step.get("text"))
            elif step_type == "wait":
                time.sleep(step.get("duration", 1))

workflow_engine = WorkflowEngine()
