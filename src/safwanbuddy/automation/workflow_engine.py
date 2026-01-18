import json
import time
from src.safwanbuddy.core.logging import logger

class WorkflowEngine:
    def __init__(self):
        self.workflows = {}
        self.is_recording = False
        self.recorded_steps = []

    def start_recording(self):
        self.is_recording = True
        self.recorded_steps = []
        logger.info("Started recording workflow.")
        # In a real implementation, we would hook into keyboard/mouse events here

    def stop_recording(self, name: str):
        self.is_recording = False
        self.workflows[name] = self.recorded_steps
        logger.info(f"Stopped recording workflow: {name}. Recorded {len(self.recorded_steps)} steps.")
        return self.recorded_steps

    def add_step(self, step_type: str, **kwargs):
        if self.is_recording:
            step = {"type": step_type, "timestamp": time.time(), **kwargs}
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
            step_type = step.get("type")
            if step_type == "click":
                click_system.click_text(step.get("target"))
            elif step_type == "type":
                type_system.type_text(step.get("text"))
            elif step_type == "wait":
                time.sleep(step.get("duration", 1))
            
            # Simulate delay between steps
            time.sleep(0.5)

workflow_engine = WorkflowEngine()
