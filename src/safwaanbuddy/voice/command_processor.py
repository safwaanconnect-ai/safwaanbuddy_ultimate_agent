"""Intent recognition and command routing."""

import logging
import re
from typing import Dict, Callable, Optional, List, Tuple
from dataclasses import dataclass

from ..core.events import EventBus, EventType


@dataclass
class Command:
    """Command definition."""
    name: str
    patterns: List[str]
    handler: Callable
    description: str = ""


class CommandProcessor:
    """Process voice commands and route to appropriate handlers."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.event_bus = EventBus()
        
        self.commands: List[Command] = []
        self._register_default_commands()
        
        self.event_bus.subscribe(EventType.VOICE_COMMAND, self._on_voice_command)
    
    def _register_default_commands(self) -> None:
        """Register default command patterns."""
        default_commands = [
            Command(
                name="open_browser",
                patterns=[
                    r"open (?:browser|chrome|firefox|edge)",
                    r"launch (?:browser|chrome|firefox|edge)",
                    r"start (?:browser|chrome|firefox|edge)"
                ],
                description="Open web browser"
            ),
            Command(
                name="search",
                patterns=[
                    r"search (?:for )?(.+)",
                    r"google (.+)",
                    r"find (.+)",
                    r"look up (.+)"
                ],
                description="Search the web"
            ),
            Command(
                name="type_text",
                patterns=[
                    r"type (.+)",
                    r"write (.+)",
                    r"enter (.+)"
                ],
                description="Type text"
            ),
            Command(
                name="click",
                patterns=[
                    r"click (?:on )?(.+)",
                    r"press (.+)",
                    r"tap (?:on )?(.+)"
                ],
                description="Click on element"
            ),
            Command(
                name="fill_form",
                patterns=[
                    r"fill (?:the )?form",
                    r"complete (?:the )?form",
                    r"auto fill"
                ],
                description="Fill form automatically"
            ),
            Command(
                name="create_document",
                patterns=[
                    r"create (?:a )?(?:word |)document(?: named (.+))?",
                    r"new (?:word |)document(?: named (.+))?",
                    r"make (?:a )?(?:word |)document(?: named (.+))?"
                ],
                description="Create Word document"
            ),
            Command(
                name="create_spreadsheet",
                patterns=[
                    r"create (?:a )?(?:excel |)spreadsheet(?: named (.+))?",
                    r"new (?:excel |)spreadsheet(?: named (.+))?",
                    r"make (?:a )?(?:excel |)spreadsheet(?: named (.+))?"
                ],
                description="Create Excel spreadsheet"
            ),
            Command(
                name="create_pdf",
                patterns=[
                    r"create (?:a )?pdf(?: named (.+))?",
                    r"generate (?:a )?pdf(?: named (.+))?",
                    r"make (?:a )?pdf(?: named (.+))?"
                ],
                description="Create PDF document"
            ),
            Command(
                name="take_screenshot",
                patterns=[
                    r"take (?:a )?screenshot",
                    r"capture (?:the )?screen",
                    r"screen capture"
                ],
                description="Take screenshot"
            ),
            Command(
                name="open_settings",
                patterns=[
                    r"open settings",
                    r"show settings",
                    r"settings"
                ],
                description="Open settings"
            ),
            Command(
                name="help",
                patterns=[
                    r"help",
                    r"what can you do",
                    r"list commands",
                    r"show commands"
                ],
                description="Show help"
            ),
            Command(
                name="stop",
                patterns=[
                    r"stop",
                    r"cancel",
                    r"abort",
                    r"quit"
                ],
                description="Stop current action"
            )
        ]
        
        for cmd in default_commands:
            self.commands.append(cmd)
    
    def register_command(self, command: Command) -> None:
        """Register a new command.
        
        Args:
            command: Command to register
        """
        self.commands.append(command)
        self.logger.info(f"Registered command: {command.name}")
    
    def unregister_command(self, name: str) -> None:
        """Unregister a command by name.
        
        Args:
            name: Command name
        """
        self.commands = [cmd for cmd in self.commands if cmd.name != name]
        self.logger.info(f"Unregistered command: {name}")
    
    def _on_voice_command(self, event) -> None:
        """Handle voice command event."""
        command_text = event.data.get("command", "").lower().strip()
        
        if not command_text:
            return
        
        self.logger.info(f"Processing command: {command_text}")
        
        matched = self._match_command(command_text)
        
        if matched:
            command, groups = matched
            self.logger.info(f"Matched command: {command.name}")
            
            if command.handler:
                try:
                    command.handler(command_text, groups)
                except Exception as e:
                    self.logger.error(f"Error executing command handler: {e}", exc_info=True)
        else:
            self.logger.warning(f"No matching command for: {command_text}")
            self.event_bus.emit(EventType.WARNING_ISSUED, {
                "message": f"Unknown command: {command_text}"
            })
    
    def _match_command(self, text: str) -> Optional[Tuple[Command, Tuple]]:
        """Match text against command patterns.
        
        Args:
            text: Command text to match
            
        Returns:
            Tuple of (Command, matched groups) or None
        """
        for command in self.commands:
            for pattern in command.patterns:
                match = re.match(pattern, text, re.IGNORECASE)
                if match:
                    return (command, match.groups())
        
        return None
    
    def get_commands(self) -> List[Command]:
        """Get all registered commands.
        
        Returns:
            List of commands
        """
        return self.commands.copy()
    
    def get_help_text(self) -> str:
        """Get help text for all commands.
        
        Returns:
            Formatted help text
        """
        lines = ["Available commands:"]
        
        for cmd in self.commands:
            if cmd.description:
                example = cmd.patterns[0] if cmd.patterns else ""
                example = re.sub(r'\(.+?\)', '[...]', example)
                example = re.sub(r'\?:', '', example)
                lines.append(f"  - {example}: {cmd.description}")
        
        return "\n".join(lines)
