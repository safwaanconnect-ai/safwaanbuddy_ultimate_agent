import os
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.core.logging import logger

class SoundManager:
    def __init__(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)
        
        self.sounds = {
            "startup": "startup.wav",
            "success": "success.wav",
            "error": "error.wav",
            "alert": "alert.wav",
            "processing": "ambient_hum.wav"
        }
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "assets", "sounds")
        self._setup_subscriptions()

    def _setup_subscriptions(self):
        event_bus.subscribe("system_state", self._on_system_state)
        event_bus.subscribe("action_result", self._on_action_result)
        event_bus.subscribe("voice_recognition_start", lambda _: self.play("startup"))

    def _on_system_state(self, state):
        if state == "processing":
            self.play("processing", loop=True)
        elif state == "idle":
            self.stop()

    def _on_action_result(self, result):
        if isinstance(result, dict):
            success = result.get("success", True)
        else:
            success = bool(result)
            
        if success:
            self.play("success")
        else:
            self.play("error")

    def play(self, sound_key, loop=False):
        if sound_key in self.sounds:
            file_path = os.path.join(self.assets_path, self.sounds[sound_key])
            if os.path.exists(file_path):
                self.player.setSource(QUrl.fromLocalFile(file_path))
                if loop:
                    self.player.setLoops(QMediaPlayer.Loops.Infinite)
                else:
                    self.player.setLoops(QMediaPlayer.Loops.Once)
                self.player.play()
                logger.info(f"Playing sound: {sound_key}")
            else:
                logger.warning(f"Sound file not found: {file_path}")

    def stop(self):
        self.player.stop()

sound_manager = SoundManager()
