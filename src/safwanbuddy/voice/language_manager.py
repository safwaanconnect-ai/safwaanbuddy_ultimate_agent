from src.safwanbuddy.profiles.language_mapper import language_mapper

class LanguageManager:
    def __init__(self):
        self.supported_languages = {
            "en": "English",
            "hi": "Hindi",
            "hyderabadi": "Hyderabadi"
        }
        self.current_language = "en"

    def process_speech(self, text: str):
        """Processes recognized speech according to current language and dialect."""
        if self.current_language in ["hyderabadi", "hi"]:
            intent, normalized = language_mapper.normalize_input(text)
            return intent, normalized
        return "unknown", text

    def get_response_greeting(self):
        return language_mapper.get_greeting(self.current_language)

    def set_language(self, lang_code: str):
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            return True
        return False

language_manager = LanguageManager()
