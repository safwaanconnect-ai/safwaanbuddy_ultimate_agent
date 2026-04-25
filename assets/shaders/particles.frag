#version 330
uniform float time;
uniform vec2 resolution;
uniform float audio_intensity;
out vec4 f_color;

float hash(float n) { return fract(sin(n) * 43758.5453123); }

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution) / min(resolution.x, resolution.y);
    
    vec3 color = vec3(0.0);
    float total_alpha = 0.0;
    
    for(float i = 0.0; i < 60.0; i++) {
        float h = hash(i);
        float speed = 0.1 + h * 0.4;
        float phase = h * 6.28;
        
        // Circular motion with audio bounce
        float radius = 0.5 + 0.2 * sin(time * 0.5 + h);
        radius *= (1.0 + audio_intensity * 0.2);
        
        vec2 p = vec2(
            sin(time * speed + phase) * radius,
            cos(time * speed * 0.8 + phase) * radius
        );
        
        float dist = length(uv - p);
        float size = 0.002 + h * 0.005;
        float glow = (0.01 + 0.01 * audio_intensity) / dist;
        
        vec3 p_color = mix(vec3(0.0, 0.5, 1.0), vec3(0.0, 1.0, 0.8), h);
        float mask = smoothstep(size + 0.1, size, dist);
        color += p_color * mask * glow;
        total_alpha += mask * glow * 0.1;
    }
    
    f_color = vec4(color, clamp(total_alpha, 0.0, 1.0));
}
