#version 330
uniform float time;
uniform vec2 resolution;
uniform float audio_intensity;
out vec4 f_color;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453123);
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
    
    // Enhanced Chromatic Aberration
    float chrom_offset = 0.005 + 0.02 * audio_intensity;
    float r = noise(uv + vec2(chrom_offset, 0.0) + time * 0.1);
    float g = noise(uv + time * 0.1);
    float b = noise(uv - vec2(chrom_offset, 0.0) + time * 0.1);
    
    // Scanline logic that reacts to audio
    float scanline = sin(uv.y * 800.0 * (1.0 + audio_intensity * 0.1) + time * 10.0);
    scanline = smoothstep(0.0, 1.0, scanline);
    
    // Dynamic Grid
    vec2 grid_uv = (uv - 0.5) * (20.0 + audio_intensity * 10.0);
    float grid = abs(sin(grid_uv.x)) * abs(sin(grid_uv.y));
    grid = pow(1.0 - grid, 10.0);
    
    // Holographic flicker
    float flicker = noise(vec2(time * 10.0, 0.0));
    flicker = step(0.1, flicker);
    
    // Main hologram color
    vec3 base_color = vec3(0.0, 0.8, 1.0);
    vec3 color = base_color * (grid * 0.2 + scanline * 0.1 + 0.4);
    
    // Apply Chromatic Aberration
    color.r += r * chrom_offset * 10.0;
    color.b += b * chrom_offset * 10.0;
    
    // Vignette
    float vig = 1.0 - length(centered_uv) * 1.2;
    color *= vig;
    
    // Vertical "ghosting" or scanning bars
    float bar = smoothstep(0.2, 0.0, abs(sin(uv.y * 2.0 + time) - 0.5));
    color += base_color * bar * 0.1 * audio_intensity;
    
    // Glitch
    float glitch = step(0.98, hash(vec2(time, 1.0)));
    color += glitch * vec3(hash(uv + time), hash(uv - time), hash(uv * time)) * 0.2;

    f_color = vec4(color, (0.6 + 0.4 * audio_intensity) * flicker * vig);
}
