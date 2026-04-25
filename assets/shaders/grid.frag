#version 330
uniform float time;
uniform vec2 resolution;
uniform float audio_intensity;
out vec4 f_color;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453123);
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec2 p = uv - 0.5;
    p.x *= resolution.x / resolution.y;
    
    // Dynamic perspective distortion
    float z = 1.0 / (p.y + 1.5);
    vec2 grid_uv = vec2(p.x * z, z + time * 0.5);
    
    // Grid lines with audio reactivity
    float thickness = 0.02 + 0.03 * audio_intensity;
    float gx = smoothstep(1.0 - thickness, 1.0, abs(sin(grid_uv.x * 20.0)));
    float gy = smoothstep(1.0 - thickness, 1.0, abs(sin(grid_uv.y * 20.0)));
    float grid = max(gx, gy);
    
    // Pulse effect
    float pulse = sin(time * 2.0) * 0.5 + 0.5;
    vec3 color = mix(vec3(0.0, 0.2, 0.4), vec3(0.0, 0.8, 1.0), grid);
    color += vec3(0.0, 0.4, 0.6) * grid * (pulse + audio_intensity);
    
    // Horizon glow
    float glow = exp(-abs(p.y + 0.1) * 5.0);
    color += vec3(0.0, 0.5, 0.8) * glow * (1.0 + audio_intensity);
    
    // Scanline
    float scan = sin(uv.y * 200.0 - time * 10.0) * 0.05;
    color += scan;
    
    // Noise/Film Grain
    color += (hash(uv + time) - 0.5) * 0.05;
    
    // Vignette
    float vig = 1.0 - length(p) * 1.2;
    color *= vig;
    
    f_color = vec4(color, 0.7 * vig);
}
