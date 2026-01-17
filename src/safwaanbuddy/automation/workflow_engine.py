"""Record and playback workflow automation."""

import logging
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager


@dataclass
class WorkflowStep:
    """Workflow step definition."""
    action: str
    params: Dict[str, Any]
    timestamp: float
    delay_after: float = 0.0


class Workflow:
    """Workflow container."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.created_at = datetime.now().isoformat()
    
    def add_step(self, step: WorkflowStep) -> None:
        """Add step to workflow."""
        self.steps.append(step)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "steps": [asdict(step) for step in self.steps]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """Create from dictionary."""
        workflow = cls(data["name"], data.get("description", ""))
        workflow.created_at = data.get("created_at", datetime.now().isoformat())
        
        for step_data in data.get("steps", []):
            step = WorkflowStep(**step_data)
            workflow.add_step(step)
        
        return workflow


class WorkflowEngine:
    """Record and playback workflow automation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.workflows_dir = Path("data/workflows")
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_workflow: Optional[Workflow] = None
        self.is_recording = False
        self.recording_start_time = 0.0
    
    def start_recording(self, name: str, description: str = "") -> None:
        """Start recording a workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
        """
        if self.is_recording:
            self.logger.warning("Already recording")
            return
        
        self.current_workflow = Workflow(name, description)
        self.is_recording = True
        self.recording_start_time = time.time()
        
        self.logger.info(f"Started recording workflow: {name}")
        self.event_bus.emit(EventType.WORKFLOW_STARTED, {"name": name})
    
    def stop_recording(self) -> Optional[Workflow]:
        """Stop recording and return workflow.
        
        Returns:
            Recorded workflow or None
        """
        if not self.is_recording:
            self.logger.warning("Not recording")
            return None
        
        self.is_recording = False
        workflow = self.current_workflow
        
        self.logger.info(f"Stopped recording workflow: {workflow.name}")
        self.event_bus.emit(EventType.WORKFLOW_RECORDED, {
            "name": workflow.name,
            "steps": len(workflow.steps)
        })
        
        return workflow
    
    def record_step(self, action: str, params: Dict[str, Any], delay_after: float = 0.0) -> None:
        """Record a workflow step.
        
        Args:
            action: Action name
            params: Action parameters
            delay_after: Delay after this step
        """
        if not self.is_recording or not self.current_workflow:
            return
        
        timestamp = time.time() - self.recording_start_time
        step = WorkflowStep(action, params, timestamp, delay_after)
        
        self.current_workflow.add_step(step)
        self.logger.debug(f"Recorded step: {action}")
    
    def save_workflow(self, workflow: Workflow, filename: Optional[str] = None) -> bool:
        """Save workflow to file.
        
        Args:
            workflow: Workflow to save
            filename: Output filename (auto-generated if None)
            
        Returns:
            True if successful
        """
        if filename is None:
            filename = f"{workflow.name.replace(' ', '_')}.json"
        
        filepath = self.workflows_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            
            self.logger.info(f"Saved workflow: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save workflow: {e}")
            return False
    
    def load_workflow(self, filename: str) -> Optional[Workflow]:
        """Load workflow from file.
        
        Args:
            filename: Workflow filename
            
        Returns:
            Loaded workflow or None
        """
        filepath = self.workflows_dir / filename
        
        if not filepath.exists():
            self.logger.error(f"Workflow not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            workflow = Workflow.from_dict(data)
            self.logger.info(f"Loaded workflow: {workflow.name}")
            return workflow
        except Exception as e:
            self.logger.error(f"Failed to load workflow: {e}")
            return None
    
    def playback_workflow(self, workflow: Workflow) -> bool:
        """Playback a recorded workflow.
        
        Args:
            workflow: Workflow to playback
            
        Returns:
            True if successful
        """
        self.logger.info(f"Playing back workflow: {workflow.name}")
        self.event_bus.emit(EventType.WORKFLOW_STARTED, {"name": workflow.name})
        
        try:
            for i, step in enumerate(workflow.steps):
                self.logger.debug(f"Executing step {i + 1}/{len(workflow.steps)}: {step.action}")
                
                self._execute_step(step)
                
                if step.delay_after > 0:
                    time.sleep(step.delay_after)
            
            self.event_bus.emit(EventType.WORKFLOW_COMPLETED, {
                "name": workflow.name,
                "steps": len(workflow.steps)
            })
            self.logger.info(f"Workflow completed: {workflow.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error playing workflow: {e}", exc_info=True)
            self.event_bus.emit(EventType.AUTOMATION_FAILED, {
                "workflow": workflow.name,
                "error": str(e)
            })
            return False
    
    def _execute_step(self, step: WorkflowStep) -> None:
        """Execute a workflow step.
        
        Args:
            step: Step to execute
        """
        pass
    
    def list_workflows(self) -> List[str]:
        """List available workflows.
        
        Returns:
            List of workflow filenames
        """
        return [f.name for f in self.workflows_dir.glob("*.json")]
