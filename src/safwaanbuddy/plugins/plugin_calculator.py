"""Calculator plugin for basic arithmetic."""

from ..plugins.plugin_loader import PluginBase


class CalculatorPlugin(PluginBase):
    """Simple calculator plugin."""
    
    @property
    def name(self):
        return "Calculator"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self):
        self.logger.info("Calculator plugin initialized")
        return True
    
    def execute(self, expression: str):
        """Evaluate arithmetic expression.
        
        Args:
            expression: Math expression to evaluate
            
        Returns:
            Result or error message
        """
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            self.logger.info(f"Calculated: {expression} = {result}")
            return result
        except Exception as e:
            self.logger.error(f"Calculation error: {e}")
            return f"Error: {e}"
