#version 330
uniform float time;
uniform vec2 resolution;
uniform float audio_intensity;
out vec4 f_color;

mat2 rotate2d(float angle) {
    return mat2(cos(angle), -sin(angle),
                sin(angle), cos(angle));
}

float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

float noise(vec2 st) {
    vec2 i = floor(st);
    vec2 f = fract(st);
    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

#define OCTAVES 6
float fbm(vec2 st) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < OCTAVES; i++) {
        value += amplitude * noise(st);
        st *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution) / min(resolution.x, resolution.y);
    
    // Rotate the entire field
    uv *= rotate2d(time * 0.2);
    
    float d = length(uv);
    
    // Fractal noise for "living" effect
    float n = fbm(uv * 3.0 + time * 0.5);
    
    float ring_width = 0.02 + audio_intensity * 0.1 + n * 0.05;
    float radius = 0.6 + 0.05 * sin(time * 2.0) + audio_intensity * 0.1;
    
    float ring = smoothstep(ring_width, 0.0, abs(d - radius));
    
    // Add multiple energy pulses with fractal influence
    float pulses = 0.0;
    for(float i = 0.0; i < 3.0; i++) {
        float angle = atan(uv.y, uv.x) + time * (1.0 + i * 0.3) + n;
        pulses += smoothstep(0.7, 1.0, sin(angle * (4.0 + i))) * ring;
    }
    
    vec3 color = vec3(0.0, 0.5, 1.0) * ring; // Deep blue base
    color += vec3(0.0, 1.0, 0.8) * pulses;  // Cyan pulses
    color += vec3(1.0) * pow(ring, 10.0);   // White core
    
    // Reactivity shift
    color.rb += audio_intensity * 0.3;
    
    f_color = vec4(color, (ring * 0.7 + pulses * 0.3) * (1.0 - d * 0.5));
}
