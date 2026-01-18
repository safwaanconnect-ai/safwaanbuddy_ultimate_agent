class LanguageManager:
    def __init__(self):
        self.supported_languages = {
            "en": "English",
            "hi": "Hindi",
            "hyderabadi": "Hyderabadi"
        }
        self.current_language = "en"

    def set_language(self, lang_code: str):
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            return True
        return False

    def get_current_language(self):
        return self.current_language

language_manager = LanguageManager()
