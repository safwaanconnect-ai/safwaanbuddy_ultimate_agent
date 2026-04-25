#version 330
uniform float time;
uniform vec2 resolution;
uniform float audio_intensity;
out vec4 f_color;

#define PI 3.14159265359

mat2 rotate(float a) {
    float s = sin(a), c = cos(a);
    return mat2(c, -s, s, c);
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution) / min(resolution.x, resolution.y);
    float d = length(uv);
    
    vec3 finalColor = vec3(0.0);
    
    // Multiple concentric rings
    for(float i = 0.0; i < 3.0; i++) {
        float speed = time * (0.5 + i * 0.2);
        vec2 uv_r = uv * rotate(speed);
        
        float ring_radius = 0.6 + i * 0.1;
        float ring_thickness = 0.01 + 0.02 * audio_intensity;
        
        // Broken ring effect
        float angle = atan(uv_r.y, uv_r.x);
        float mask = step(0.5, sin(angle * 5.0 + speed));
        
        float ring = smoothstep(ring_thickness, 0.0, abs(d - ring_radius));
        vec3 col = mix(vec3(1.0, 0.0, 0.4), vec3(1.0, 0.6, 0.0), i / 3.0);
        
        finalColor += col * ring * mask * (1.0 + audio_intensity * 2.0);
    }
    
    // Central core
    float core = smoothstep(0.2 + 0.1 * audio_intensity, 0.0, d);
    finalColor += vec3(1.0, 0.8, 0.2) * core * (sin(time * 10.0) * 0.2 + 0.8);
    
    // Background glow
    finalColor += vec3(0.5, 0.0, 0.2) * (0.1 / d) * (1.0 + audio_intensity);
    
    f_color = vec4(finalColor, clamp(length(finalColor), 0.0, 0.9));
}
