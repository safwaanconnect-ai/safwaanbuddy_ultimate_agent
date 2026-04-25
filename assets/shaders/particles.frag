#version 330
uniform float time;
uniform vec2 resolution;
out vec4 f_color;

float hash(float n) { return fract(sin(n) * 43758.5453123); }

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution) / min(resolution.x, resolution.y);
    
    vec3 color = vec3(0.0);
    
    for(float i = 0.0; i < 50.0; i++) {
        float h = hash(i);
        float speed = 0.2 + h * 0.5;
        float phase = h * 6.28;
        
        vec2 p = vec2(
            sin(time * speed + phase),
            cos(time * speed * 0.7 + phase)
        );
        
        float dist = length(uv - p);
        float size = 0.005 + h * 0.01;
        float glow = 0.02 / dist;
        
        vec3 p_color = vec3(0.1, 0.5, 1.0) * h + vec3(0.0, 0.8, 1.0) * (1.0 - h);
        color += p_color * smoothstep(size + 0.1, size, dist) * glow;
    }
    
    f_color = vec4(color, 1.0);
}
