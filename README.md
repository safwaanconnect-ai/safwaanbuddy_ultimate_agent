# SafwanBuddy Ultimate++ v7.0 (Production)

[![Version](https://img.shields.io/badge/version-7.0%20Ultimate-blue.svg)](https://github.com/your-repo/safwanbuddy)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-repo/safwanbuddy/actions)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://www.python.org/)

## Human-Digital Symbiosis System

SafwanBuddy Ultimate++ is a state-of-the-art human-digital symbiosis system. It bridges the gap between human intent and digital execution through an immersive, AI-driven interface. Featuring advanced computer vision, offline voice recognition, and autonomous task chaining.

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
- **State Persistence:** Logs execution history to `config/expert_history.json`.
- **Unique Visual Aura:** Triggers specialized "Energy Ring" shader effects during execution.

### 🌌 Premium AV Experience (SoundManager Pro)
- **Advanced Shaders:** Fractal noise (FBM), rotation matrices, chromatic aberration, and dynamic scanning lines.
- **Cross-Fading Audio:** Seamless transitions between ambient background loops (Idle vs. Processing).
- **Sub-millisecond Latency:** Visuals respond instantly to voice intensity changes.

### 🤖 Multilingual Voice AI
- **Vosk Integration:** Full offline speech-to-text recognition.
- **Dialect Support:** Specialized support for English, Hindi, and Hyderabadi slang.

---

## 🛠 Technical Deep Dive

### Event-Driven Architecture
SafwanBuddy utilizes a central `event_bus` (Observer Pattern) to decouple subsystems.
```python
# Emitting an event
event_bus.emit("expert_task_request", "research and report about quantum computing")
```

### Shader Pipeline
The UI leverages **ModernGL** for high-performance GPU rendering.
- **Vertex Shaders:** Handle geometry and screen projection.
- **Fragment Shaders:** Calculate per-pixel colors with complex GLSL math.

---

## 📦 Installation & Build

### Prerequisites
- **Python 3.9+**
- **Tesseract OCR:** Required for screen text recognition.
- **Vosk Models:** Place in `assets/models/`.

### Setup
```bash
git clone https://github.com/your-repo/safwanbuddy.git
cd safwanbuddy
pip install -r requirements.txt
python main.py
```

### Build Production EXE
To generate a standalone executable:
```bash
python build_exe.py
```
*The output will be in the `dist/SafwanBuddy` directory.*

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

**Author:** Safwan & The AI Team  
**Contact:** dev@safwanbuddy.ai
