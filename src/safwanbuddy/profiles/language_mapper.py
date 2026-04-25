class LanguageMapper:
    def __init__(self):
        # Hyderabadi/Hindi dialect mapping to system intents
        self.mappings = {
            "hau": "yes",
            "nakko": "no",
            "kaiku": "why",
            "kaisa hai": "how are you",
            "kya karre": "what are you doing",
            "kya hona": "what do you want",
            "ich": "", # emphasis suffix, often can be ignored or used for context
            "potti": "girl",
            "potta": "boy",
            "baigan": "nonsense/ignore", # used in various contexts
            "hallu": "slowly",
            "jaldi": "quickly",
            "shabaash": "well done",
            "khamosh": "quiet",
            "sunno": "listen",
            "batao": "tell/show",
            "khol": "open",
            "band kar": "close"
        }
        
        self.intent_patterns = {
            "open_browser": ["browser khol", "internet chalao", "net khol"],
            "search": ["dhundo", "search karo", "pata karo"],
            "generate_report": ["report banao", "paper banao", "document likho"],
            "status_check": ["kya chalra", "status kya hai", "kaam kahan tak pahuncha"],
            "shutdown": ["chalo khuda hafiz", "band karo", "so jao"]
        }

    def normalize_input(self, text: str):
        text = text.lower().strip()
        
        # Replace specific dialect words
        words = text.split()
        normalized_words = [self.mappings.get(w, w) for w in words]
        normalized_text = " ".join(normalized_words)
        
        # Check for intent patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text or pattern in normalized_text:
                    return intent, text
                    
        return "unknown", text

    def get_greeting(self, language="hyderabadi"):
        if language == "hyderabadi":
            return "Salaam! Kya hona bolo aapku?"
        elif language == "hindi":
            return "Namaste! Main aapki kya madad kar sakta hoon?"
        return "Hello! How can I help you today?"

language_mapper = LanguageMapper()
