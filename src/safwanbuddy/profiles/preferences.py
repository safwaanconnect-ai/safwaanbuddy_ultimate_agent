from src.safwanbuddy.core import config_manager

class Preferences:
    def __init__(self):
        self.config = config_manager

    def get_voice_language(self):
        return self.config.get("voice.language", "en")

    def set_voice_language(self, lang: str):
        # In a real app, this would update the config file
        pass

    def is_human_like_typing_enabled(self):
        return self.config.get("automation.human_like", True)

preferences = Preferences()
