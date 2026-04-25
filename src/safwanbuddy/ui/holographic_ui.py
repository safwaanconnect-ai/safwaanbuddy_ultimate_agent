from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import QTimer
import moderngl
import numpy as np
import os
from src.safwanbuddy.core import event_bus

class HolographicUI(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctx = None
        self.progs = {}
        self.active_prog_name = "hologram"
        self.vbo = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS
        self.time = 0
        self.audio_intensity = 0.0
        
        event_bus.subscribe("system_state", self.on_state_change)
        event_bus.subscribe("audio_level", self.on_audio_level)

    def on_state_change(self, state):
        if state == "listening":
            self.active_prog_name = "hologram"
        elif state == "processing":
            self.active_prog_name = "particles"
        else:
            self.active_prog_name = "hologram"

    def on_audio_level(self, level):
        self.audio_intensity = level

    def load_shader(self, name):
        vert_path = f"assets/shaders/grid.vert"
        frag_path = f"assets/shaders/{name}.frag"
        
        if os.path.exists(vert_path) and os.path.exists(frag_path):
            with open(vert_path, 'r') as f:
                vert_code = f.read()
            with open(frag_path, 'r') as f:
                frag_code = f.read()
        else:
            # Fallback (simplified version of hologram)
            vert_code = '''
                #version 330
                in vec2 in_vert;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            '''
            frag_code = '''
                #version 330
                uniform float time;
                uniform vec2 resolution;
                out vec4 f_color;
                void main() {
                    vec2 uv = gl_FragCoord.xy / resolution;
                    f_color = vec4(0.0, 0.5 * sin(time + uv.x), 0.8, 0.5);
                }
            '''
        
        return self.ctx.program(vertex_shader=vert_code, fragment_shader=frag_code)

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        
        for name in ["hologram", "particles", "grid"]:
            try:
                self.progs[name] = self.load_shader(name)
            except Exception as e:
                print(f"Failed to load shader {name}: {e}")

        vertices = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        
        self.vaos = {}
        for name, prog in self.progs.items():
            self.vaos[name] = self.ctx.simple_vertex_array(prog, self.vbo, 'in_vert')

    def paintGL(self):
        if not self.ctx or self.active_prog_name not in self.progs: return
        self.ctx.clear(0.1, 0.1, 0.1, 1.0)
        self.time += 0.05
        
        prog = self.progs[self.active_prog_name]
        vao = self.vaos[self.active_prog_name]
        
        if 'time' in prog:
            prog['time'].value = self.time
        if 'resolution' in prog:
            prog['resolution'].value = (float(self.width()), float(self.height()))
        if 'audio_intensity' in prog:
            prog['audio_intensity'].value = self.audio_intensity
            
        vao.render(moderngl.TRIANGLE_STRIP)

    def resizeGL(self, width, height):
        if self.ctx:
            self.ctx.viewport = (0, 0, width, height)
