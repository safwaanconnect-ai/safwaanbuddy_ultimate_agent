import os
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, QTimer
from src.safwanbuddy.core.events import event_bus
from src.safwanbuddy.core.logging import logger

class SoundManager:
    def __init__(self):
        # Sound Effects Player
        self.fx_player = QMediaPlayer()
        self.fx_output = QAudioOutput()
        self.fx_player.setAudioOutput(self.fx_output)
        self.fx_output.setVolume(0.8)
        
        # Background/Ambient Players for Cross-fading
        self.bg_player_a = QMediaPlayer()
        self.bg_output_a = QAudioOutput()
        self.bg_player_a.setAudioOutput(self.bg_output_a)
        
        self.bg_player_b = QMediaPlayer()
        self.bg_output_b = QAudioOutput()
        self.bg_player_b.setAudioOutput(self.bg_output_b)
        
        self.active_player = self.bg_player_a
        self.active_output = self.bg_output_a
        self.inactive_player = self.bg_player_b
        self.inactive_output = self.bg_output_b
        
        self.sounds = {
            "startup": "startup.wav",
            "success": "success.wav",
            "error": "error.wav",
            "alert": "alert.wav",
            "processing": "ambient_hum.wav",
            "idle": "idle_hum.wav"
        }
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "assets", "sounds")
        self._setup_subscriptions()
        
        # Fading state
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self._handle_fade)
        self.fade_steps = 20
        self.current_step = 0
        self.target_bg_volume = 0.5

    def _setup_subscriptions(self):
        event_bus.subscribe("system_state", self._on_system_state)
        event_bus.subscribe("action_result", self._on_action_result)
        event_bus.subscribe("voice_recognition_start", lambda _: self.play_fx("startup"))

    def _on_system_state(self, state):
        if state in ["processing", "processing_expert"]:
            self.play_bg("processing", volume=0.5)
        elif state == "idle":
            self.play_bg("idle", volume=0.2)

    def _on_action_result(self, result):
        if isinstance(result, dict):
            success = result.get("success", True)
        else:
            success = bool(result)
            
        if success:
            self.play_fx("success")
        else:
            self.play_fx("error")

    def play_fx(self, sound_key):
        if sound_key in self.sounds:
            file_path = os.path.join(self.assets_path, self.sounds[sound_key])
            if os.path.exists(file_path):
                self.fx_player.setSource(QUrl.fromLocalFile(file_path))
                self.fx_player.play()
            else:
                logger.warning(f"FX Sound file not found: {file_path}")

    def play_bg(self, sound_key, volume=0.5):
        if sound_key not in self.sounds:
            return
            
        file_path = os.path.join(self.assets_path, self.sounds[sound_key])
        if not os.path.exists(file_path):
            logger.warning(f"BG Sound file not found: {file_path}")
            return

        # Prepare inactive player
        self.inactive_player.setSource(QUrl.fromLocalFile(file_path))
        self.inactive_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.inactive_output.setVolume(0.0)
        self.inactive_player.play()
        
        self.initial_active_volume = self.active_output.volume()
        self.target_bg_volume = volume
        self.current_step = 0
        self.fade_timer.start(50) # 50ms steps

    def _handle_fade(self):
        self.current_step += 1
        progress = self.current_step / self.fade_steps
        
        # Fade in new, fade out old
        self.inactive_output.setVolume(progress * self.target_bg_volume)
        self.active_output.setVolume((1.0 - progress) * self.initial_active_volume)
        
        if self.current_step >= self.fade_steps:
            self.fade_timer.stop()
            self.active_player.stop()
            # Swap
            self.active_player, self.inactive_player = self.inactive_player, self.active_player
            self.active_output, self.inactive_output = self.inactive_output, self.active_output
            logger.info("Background sound transition complete.")

    def stop_all(self):
        self.fx_player.stop()
        self.bg_player_a.stop()
        self.bg_player_b.stop()

sound_manager = SoundManager()
