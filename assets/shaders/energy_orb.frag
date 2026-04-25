#version 330
uniform float time;
uniform vec2 resolution;
uniform float audio_intensity;
out vec4 f_color;

float sphere(vec3 p, float r) {
    return length(p) - r;
}

float map(vec3 p) {
    float s = sphere(p, 1.0 + 0.1 * sin(p.x * 5.0 + time * 2.0) * sin(p.y * 5.0 + time * 3.0) * (1.0 + audio_intensity * 5.0));
    return s;
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * resolution.xy) / min(resolution.y, resolution.x);
    vec3 ro = vec3(0.0, 0.0, -3.0);
    vec3 rd = normalize(vec3(uv, 1.0));
    
    float t = 0.0;
    for(int i = 0; i < 64; i++) {
        vec3 p = ro + rd * t;
        float d = map(p);
        if(d < 0.01) break;
        t += d;
        if(t > 10.0) break;
    }
    
    vec3 col = vec3(0.0);
    if(t < 10.0) {
        vec3 p = ro + rd * t;
        vec3 n = normalize(vec3(
            map(p + vec3(0.01, 0.0, 0.0)) - map(p - vec3(0.01, 0.0, 0.0)),
            map(p + vec3(0.0, 0.01, 0.0)) - map(p - vec3(0.0, 0.01, 0.0)),
            map(p + vec3(0.0, 0.0, 0.01)) - map(p - vec3(0.0, 0.0, 0.01))
        ));
        float diff = max(dot(n, normalize(vec3(1.0, 1.0, -1.0))), 0.0);
        col = vec3(0.1, 0.4, 0.8) * diff + vec3(0.0, 0.2, 0.5);
        col += pow(1.0 - max(dot(n, -rd), 0.0), 3.0) * vec3(0.5, 0.8, 1.0); // Rim lighting
    }
    
    // Background glow
    col += vec3(0.0, 0.1, 0.3) * (1.0 / (1.0 + length(uv) * 2.0));
    
    f_color = vec4(col, 1.0);
}
