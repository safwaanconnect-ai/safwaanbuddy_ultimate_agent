#ifdef GL_ES
precision mediump float;
#endif

uniform float time;
uniform vec2 resolution;

varying vec2 v_texcoord;

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution.xy) / min(resolution.x, resolution.y);
    
    float d = length(uv);
    
    // Swirling effect
    float angle = atan(uv.y, uv.x) + time * 2.0;
    float dist = length(uv);
    
    vec3 color = vec3(0.0);
    
    // Core energy orb
    float orb = 0.5 / dist;
    orb *= (1.0 + 0.2 * sin(angle * 5.0 + time * 3.0));
    
    // Pink and Blue layers
    vec3 pink = vec3(1.0, 0.07, 0.57); // Deep Pink
    vec3 blue = vec3(0.0, 0.75, 1.0);  // Deep Sky Blue
    
    float mixFactor = 0.5 + 0.5 * sin(angle + time);
    vec3 baseColor = mix(pink, blue, mixFactor);
    
    color = baseColor * orb;
    
    // Add some "swirl" trails
    for(float i = 1.0; i < 4.0; i++) {
        uv += vec2(0.2 * sin(time + i * angle), 0.2 * cos(time + i * angle));
        color += 0.05 * baseColor / length(uv);
    }
    
    // Edge glow
    color += 0.1 * blue / (1.0 - dist);
    
    // Transparency based on intensity
    float alpha = clamp(length(color), 0.0, 0.8);
    
    gl_FragColor = vec4(color, alpha);
}
