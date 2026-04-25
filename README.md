# SafwanBuddy Ultimate++ v7.0

[![Version](https://img.shields.io/badge/version-7.0%20Ultimate-blue.svg)](https://github.com/your-repo/safwanbuddy)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-repo/safwanbuddy/actions)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://www.python.org/)

## Human-Digital Symbiosis System

SafwanBuddy Ultimate++ is an advanced human-digital symbiosis system designed to serve as an intelligent automation assistant. It integrates voice AI, computer vision, web automation, and holographic interfaces into a unified, event-driven platform.

---

## 📸 Media Gallery

| **Holographic Command Center** | **Voice Spectrum Visualizer** | **Autonomous Expert Mode** |
|:---:|:---:|:---:|
| ![Hologram](https://placehold.co/600x400/00d4ff/ffffff?text=Holographic+UI) | ![Visualizer](https://placehold.co/600x400/00ff88/ffffff?text=Audio+Visualizer) | ![Expert](https://placehold.co/600x400/ff0055/ffffff?text=Expert+Mode) |
| *Premium GLSL Shaders* | *Real-time Audio Reactivity* | *Complex Task Chaining* |

---

## 🚀 Key Features

### 🧠 Autonomous Expert Mode
The pinnacle of SafwanBuddy's automation. Decomposes high-level goals into multi-domain execution chains.
- **Cross-Domain Workflows:** (Web → Document → Social)
- **Dynamic Task Decomposition:** Uses regex and keyword weighting to break down complex strings.
- **State Persistence:** Logs execution history to `config/expert_history.json` and can recover from failure points.
- **Unique Visual Aura:** Triggers specialized "Energy Ring" shader effects during execution.

### 🌌 Premium AV Experience
- **Advanced Shaders:** Fractal noise (FBM), rotation matrices, chromatic aberration, and dynamic scanning lines.
- **SoundManager Pro:** Cross-fading mechanism for seamless transitions between ambient background loops (Idle vs. Processing).
- **Audio Reactivity:** Visualizer and shaders respond with sub-millisecond latency to voice intensity.

### 🤖 Multilingual Voice AI
- **Vosk Integration:** Full offline speech-to-text recognition.
- **Dialect Support:** Specialized support for English, Hindi, and Hyderabadi slang.
- **Natural Language:** Context-aware intent recognition for hands-free operation.

---

## 🛠 Technical Deep Dive

### Event-Driven Architecture
SafwanBuddy utilizes a central `event_bus` (Observer Pattern) to decouple subsystems. This ensures that adding a new module doesn't require modifying the core orchestrator.
```python
# Subscribing to an event
event_bus.subscribe("system_state", sound_manager._on_system_state)

# Emitting an event
event_bus.emit("web_request", {"action": "search", "query": "AI news"})
```

### Shader Pipeline
The UI leverages **ModernGL** for high-performance rendering, offloading visual computations to the GPU.
- **Vertex Shaders:** Handle geometry and screen projection.
- **Fragment Shaders:** Calculate per-pixel colors with complex GLSL math for glows, grids, and glitches.
- **Audio Uniforms:** Shaders accept `audio_intensity` as a uniform, allowing visuals to "pulse" with the user's voice.

### Plugin System
Extend SafwanBuddy's capabilities by dropping new modules into the `plugins/` directory. Each plugin can subscribe to and emit events on the global bus, allowing for community-driven feature expansion.

---

## 📂 Project Structure

```
SafwanBuddy/
├── src/safwanbuddy/
│   ├── core/           # Event Bus, Logging, Config
│   ├── ui/             # Holographic UI, Sound Manager, Shaders
│   ├── automation/     # Expert Mode, Workflow Engine, Typing
│   ├── voice/          # Vosk Recognition, TTS
│   ├── web/            # Selenium Browser Automation
│   └── vision/         # Screen Capture, OCR (Tesseract)
├── assets/
│   ├── shaders/        # GLSL Fragment & Vertex code
│   ├── sounds/         # WAV loops and FX
│   └── icons/          # App branding
├── config/             # User profiles and history
└── build_exe.py        # Production build script
```

---

## 📦 Installation & Build

### Prerequisites
- **Python 3.9+**
- **Tesseract OCR:** Required for screen text recognition.
- **Vosk Models:** Download and place in `data/models/`.

### Setup
```bash
# Clone the repository
git clone https://github.com/your-repo/safwanbuddy.git
cd safwanbuddy

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Build Production EXE
To generate a standalone executable that bundles all assets:
```bash
python build_exe.py
```
*Check the `dist/` folder for the output.*

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

**Author:** Safwan & The AI Team  
**Contact:** dev@safwanbuddy.ai
