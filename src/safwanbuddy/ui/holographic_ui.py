from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import QTimer
import moderngl
import numpy as np
import os

class HolographicUI(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctx = None
        self.prog = None
        self.vbo = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS
        self.time = 0

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        
        vert_path = "assets/shaders/grid.vert"
        frag_path = "assets/shaders/grid.frag"
        
        # Fallback if files don't exist
        if os.path.exists(vert_path) and os.path.exists(frag_path):
            with open(vert_path, 'r') as f:
                vert_code = f.read()
            with open(frag_path, 'r') as f:
                frag_code = f.read()
        else:
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
                
                float hash(vec2 p) {
                    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
                }
                
                void main() {
                    vec2 uv = gl_FragCoord.xy / resolution;
                    vec2 centered_uv = uv - 0.5;
                    
                    // Grid effect
                    float grid = abs(sin(uv.x * 40.0 + time * 0.2)) * abs(sin(uv.y * 40.0 - time * 0.1));
                    grid = pow(grid, 0.05);
                    
                    // Scanning line
                    float scan = smoothstep(0.98, 1.0, sin(uv.y * 10.0 - time * 2.0));
                    
                    // Vignette
                    float vignette = 1.0 - length(centered_uv) * 1.2;
                    
                    // Glitch/Noise
                    float noise = hash(uv + time) * 0.05;
                    
                    vec3 base_color = vec3(0.0, 0.5, 0.8);
                    vec3 color = base_color * grid * 0.4;
                    color += base_color * scan * 0.3;
                    color += noise;
                    color *= vignette;
                    
                    // Inner glow
                    color += vec3(0.0, 0.1, 0.2) * (1.0 - grid);
                    
                    f_color = vec4(color, 0.7);
                }
            '''

        self.prog = self.ctx.program(
            vertex_shader=vert_code,
            fragment_shader=frag_code
        )
        vertices = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def paintGL(self):
        if not self.ctx: return
        self.ctx.clear(0.1, 0.1, 0.1, 1.0)
        self.time += 0.05
        if 'time' in self.prog:
            self.prog['time'].value = self.time
        if 'resolution' in self.prog:
            self.prog['resolution'].value = (float(self.width()), float(self.height()))
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def resizeGL(self, width, height):
        if self.ctx:
            self.ctx.viewport = (0, 0, width, height)
