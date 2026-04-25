from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.automation import click_system, type_system, workflow_engine, form_filler, expert_mode_engine, window_manager
from src.safwanbuddy.ui.sound_manager import sound_manager
from src.safwanbuddy.voice import command_processor
from src.safwanbuddy.social.unified_interface import social_integrator
from src.safwanbuddy.web import browser_controller, search_engine, price_comparison
from src.safwanbuddy.documents import word_generator, excel_generator, pdf_generator, powerpoint_generator
from src.safwanbuddy.core.config import config_manager
from src.safwanbuddy.profiles.profile_manager import profile_manager
from src.safwanbuddy.voice.speech_recognition import VoiceRecognizer
import threading
import time
import sys
import os

class SafwanBuddyOrchestrator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SafwanBuddyOrchestrator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.subsystems = {}
        self.voice_recognizer = VoiceRecognizer()
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        event_bus.subscribe("automation_request", self._handle_automation)
        event_bus.subscribe("social_request", self._handle_social)
        event_bus.subscribe("document_request", self._handle_document)
        event_bus.subscribe("web_request", self._handle_web)
        event_bus.subscribe("system_control", self._handle_system_control)
        event_bus.subscribe("system_state", self._handle_state_change)
        event_bus.subscribe("expert_task_request", self._handle_expert_task)

    def _handle_system_control(self, data):
        # This is already handled in window_manager.py but we can add orchestrator-level logic here
        pass

    def _handle_expert_task(self, goal):
        expert_mode_engine.plan_and_execute(goal)

    def _handle_state_change(self, state):
        logger.info(f"System state: {state}")

    def start(self):
        logger.info("Orchestrator initializing subsystems...")
        # Start voice recognition in a separate thread
        voice_thread = threading.Thread(target=self.voice_recognizer.start_listening, daemon=True)
        voice_thread.start()
        logger.info("Subsystems online.")
        return True

    def _handle_automation(self, data):
        action = data.get("action")
        logger.info(f"Orchestrator action: {action}")
        
        if action == "open_browser":
            browser_controller.launch()
        elif action == "search":
            search_engine.search(data.get("query"))
        elif action == "type_profile":
            field = data.get("field")
            # Get from active profile
            profile_id = profile_manager.active_profile_id
            profile = profile_manager.get_profile(profile_id)
            if profile and field in profile:
                type_system.type_text(profile[field])
        elif action == "click_text":
            click_system.click_text(data.get("text"))
        elif action == "record_workflow":
            workflow_engine.start_recording()
        elif action == "stop_recording":
            workflow_engine.stop_recording("last_recorded")
        elif action == "run_workflow":
            workflow_engine.run_workflow(data.get("name", "workflow.json"))
        elif action == "fill_form":
            profile_id = profile_manager.active_profile_id
            profile = profile_manager.get_profile(profile_id)
            if profile:
                form_filler.start_guided_fill(profile)
        elif action == "list_windows":
            windows = window_manager.list_windows()
            logger.info(f"Found {len(windows)} visible windows.")
        elif action == "flush_dns":
            logger.info("Flushing DNS cache...")
            if sys.platform == 'win32':
                import os
                os.system("ipconfig /flushdns")
        elif action == "clear_temp":
            logger.info("Clearing temporary files...")
            if sys.platform == 'win32':
                import os
                os.system('del /q /f /s %TEMP%\\*')

    def _handle_social(self, data):
        action = data.get("action")
        if action == "call":
            social_integrator.initiate_call(data.get("name"))
        elif action == "message":
            social_integrator.send_message(data.get("name"), data.get("message"))

    def _handle_document(self, data):
        action = data.get("action")
        topic = data.get("topic", "General")
        if action == "generate_report":
            content = [
                {"type": "heading", "level": 1, "text": f"SafwanBuddy Intelligence Report: {topic}"},
                {"type": "paragraph", "text": f"Generated on {time.ctime()}"},
                {"type": "paragraph", "text": f"This report contains collected intelligence regarding: {topic}"},
                {"type": "heading", "level": 2, "text": "Activity Logs"},
                {"type": "bullet", "text": "Web search initiated."},
                {"type": "bullet", "text": "Price comparison analyzed."},
                {"type": "bullet", "text": "System metrics verified."}
            ]
            
            # If search results are available, add them
            if "search_results" in expert_mode_engine.shared_memory:
                content.append({"type": "heading", "level": 2, "text": "Extracted Data"})
                content.append({"type": "paragraph", "text": expert_mode_engine.shared_memory["search_results"]})

            filename = f"Report_{topic.replace(' ', '_')}_{int(time.time())}.docx"
            word_generator.create_document(f"Intelligence: {topic}", content, filename)
            
            pdf_filename = filename.replace(".docx", ".pdf")
            pdf_generator.create_pdf(f"Intelligence: {topic}", [c["text"] for c in content if "text" in c], pdf_filename)

            pptx_filename = f"Presentation_{topic.replace(' ', '_')}_{int(time.time())}.pptx"
            slides = [{"title": f"Intelligence: {topic}", "content": [c["text"] for c in content if c["type"] == "bullet"]}]
            powerpoint_generator.create_presentation(f"Intelligence Report: {topic}", slides, os.path.join("output/presentations", pptx_filename))

    def _handle_web(self, data):
        action = data.get("action")
        if action == "compare_price":
            price_comparison.compare_prices(data.get("product"))
        elif action == "search":
            search_engine.search(data.get("query"))

    def process_command(self, text: str):
        event_bus.emit("voice_command", text)

    def stop(self):
        logger.info("Shutting down...")
        self.voice_recognizer.stop_listening()
        browser_controller.close()
        return True

orchestrator = SafwanBuddyOrchestrator()
