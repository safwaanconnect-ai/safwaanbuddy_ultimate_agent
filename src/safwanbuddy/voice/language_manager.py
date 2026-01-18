class LanguageManager:
    def __init__(self):
        self.supported_languages = {
            "en": "English",
            "hi": "Hindi",
            "hyderabadi": "Hyderabadi"
        }
        self.current_language = "en"
        self.hyderabadi_mappings = {
            "kaiku": "kyun",
            "hallu": "dheere",
            "nakko": "nahin",
            "hau": "haan"
        }

    def translate_hyderabadi(self, text: str) -> str:
        if self.current_language != "hyderabadi":
            return text
        
        words = text.split()
        translated_words = [self.hyderabadi_mappings.get(word.lower(), word) for word in words]
        return " ".join(translated_words)

    def set_language(self, lang_code: str):
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            return True
        return False

    def get_current_language(self):
        return self.current_language

language_manager = LanguageManager()
