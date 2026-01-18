from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import QTimer
import moderngl
import numpy as np

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
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform float time;
                out vec4 f_color;
                void main() {
                    vec2 uv = gl_FragCoord.xy / vec2(1000.0, 700.0); // Rough estimate, should be uniform
                    float grid = abs(sin(uv.x * 50.0 + time)) * abs(sin(uv.y * 50.0));
                    grid = pow(grid, 0.1);
                    vec3 color = vec3(0.0, 0.8, 1.0) * grid * 0.5;
                    color += vec3(0.0, 0.2, 0.4); // Background glow
                    f_color = vec4(color, 0.6);
                }
            '''
        )
        vertices = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def paintGL(self):
        self.ctx.clear(0.1, 0.1, 0.1, 1.0)
        self.time += 0.05
        if 'time' in self.prog:
            self.prog['time'].value = self.time
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def resizeGL(self, width, height):
        self.ctx.viewport = (0, 0, width, height)
