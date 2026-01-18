#version 330
uniform float time;
out vec4 f_color;
void main() {
    vec2 uv = gl_FragCoord.xy / vec2(1000.0, 700.0);
    float grid = abs(sin(uv.x * 50.0 + time)) * abs(sin(uv.y * 50.0));
    grid = pow(grid, 0.1);
    vec3 color = vec3(0.0, 0.8, 1.0) * grid * 0.5;
    color += vec3(0.0, 0.2, 0.4);
    f_color = vec4(color, 0.6);
}
