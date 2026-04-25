#version 330
uniform float time;
uniform vec2 resolution;
uniform float audio_intensity;
out vec4 f_color;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    vec2 centered_uv = uv - 0.5;
    
    // Distort UVs based on audio and time
    float distortion = noise(uv * 10.0 + time) * 0.02 * audio_intensity;
    uv += distortion;
    
    // Grid effect
    vec2 grid_uv = uv * 40.0;
    float grid = abs(sin(grid_uv.x + time * 0.2)) * abs(sin(grid_uv.y - time * 0.1));
    grid = pow(grid, 0.05);
    
    // Neon glow lines
    float line = abs(sin(uv.y * 10.0 - time * 2.0));
    line = smoothstep(0.98, 1.0, line);
    
    // FBM-like noise for holographic feel
    float n = 0.0;
    n += noise(uv * 5.0 + time * 0.5) * 0.5;
    n += noise(uv * 10.0 - time * 0.3) * 0.25;
    
    // Color scheme: Premium Neon Cyan/Blue
    vec3 base_color = vec3(0.0, 0.8, 1.0);
    vec3 color = base_color * grid * 0.5;
    color += base_color * line * 0.5;
    color += base_color * n * 0.2;
    
    // Audio reactivity
    color *= (1.0 + audio_intensity * 0.5);
    
    // Scanning line
    float scan = smoothstep(0.99, 1.0, sin(uv.y * 50.0 - time * 5.0));
    color += vec3(1.0) * scan * 0.2;
    
    // Vignette
    float vignette = 1.0 - length(centered_uv) * 1.5;
    color *= vignette;
    
    // Glitch effect
    if (hash(vec2(time)) > 0.98) {
        color.r = mix(color.r, hash(uv + time), 0.2);
    }
    
    f_color = vec4(color, 0.7 + n * 0.3);
}
