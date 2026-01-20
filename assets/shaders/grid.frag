#version 330
uniform float time;
out vec4 f_color;

void main() {
    vec2 uv = gl_FragCoord.xy / vec2(1000.0, 700.0);
    
    // Wave effect
    float wave = sin(uv.x * 10.0 + time) * 0.1;
    uv.y += wave;
    
    // Grid pattern
    float grid_x = smoothstep(0.95, 1.0, abs(sin(uv.x * 40.0)));
    float grid_y = smoothstep(0.95, 1.0, abs(sin(uv.y * 40.0)));
    float grid = max(grid_x, grid_y);
    
    // Moving particles (scanline effect)
    float scanline = sin(uv.y * 100.0 - time * 5.0) * 0.1 + 0.1;
    
    vec3 color = vec3(0.0, 0.6, 0.8) * grid; // Neon blue grid
    color += vec3(0.0, 0.1, 0.3); // Deep blue background
    color += vec3(0.0, 0.3, 0.5) * scanline; // Moving scanlines
    
    // Vignette
    float vignette = 1.0 - length(uv - 0.5) * 1.5;
    color *= vignette;
    
    f_color = vec4(color, 0.8);
}
