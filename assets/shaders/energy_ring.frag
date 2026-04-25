#version 330
uniform float time;
uniform vec2 resolution;
uniform float audio_intensity;
out vec4 f_color;

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution) / min(resolution.x, resolution.y);
    float d = length(uv);
    
    float ring_width = 0.02 + audio_intensity * 0.05;
    float radius = 0.6 + 0.05 * sin(time * 3.0);
    
    float ring = smoothstep(ring_width, 0.0, abs(d - radius));
    
    // Add some "energy" pulses
    float pulse = 0.0;
    for(float i = 0.0; i < 4.0; i++) {
        float angle = atan(uv.y, uv.x) + time * (1.0 + i * 0.5);
        pulse += smoothstep(0.5, 1.0, sin(angle * 3.0)) * ring;
    }
    
    vec3 color = vec3(0.0, 0.7, 1.0) * ring;
    color += vec3(1.0) * pulse * 0.5;
    
    f_color = vec4(color, ring * 0.8);
}
