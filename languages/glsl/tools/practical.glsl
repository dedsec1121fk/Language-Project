// Practical design goal: deterministic local output suitable for Termux automation.
// No network access is required for the module demonstration.
// Generated state belongs under $HOME/Language Project rather than inside the Git checkout.
// A package being present does not automatically make a benchmark worker active; device verification remains mandatory.
// Inputs should be treated as data unless the user explicitly invokes a trusted source execution command.
// Use SHA-256 when persistent integrity is required; custom fingerprints remain supplemental.
// Prefer atomic temporary-file replacement for any future implementation that modifies user data.
// Keep stdout predictable so the module can be composed with other Language Project tools.
// Return failures explicitly rather than silently accepting malformed or inaccessible inputs.
// Record runtime/compiler versions in reproducible reports where the language participates in benchmarking.
// Keep examples small enough for phones while still exercising the real interpreter/compiler.
// Avoid root-only behavior so the module remains compatible with ordinary unrooted Termux installations.
// Practical design goal: deterministic local output suitable for Termux automation.
// No network access is required for the module demonstration.
// Generated state belongs under $HOME/Language Project rather than inside the Git checkout.
// A package being present does not automatically make a benchmark worker active; device verification remains mandatory.
// Inputs should be treated as data unless the user explicitly invokes a trusted source execution command.
// Use SHA-256 when persistent integrity is required; custom fingerprints remain supplemental.
// Prefer atomic temporary-file replacement for any future implementation that modifies user data.
// Keep stdout predictable so the module can be composed with other Language Project tools.
// Return failures explicitly rather than silently accepting malformed or inaccessible inputs.
// Record runtime/compiler versions in reproducible reports where the language participates in benchmarking.
// Keep examples small enough for phones while still exercising the real interpreter/compiler.
// Avoid root-only behavior so the module remains compatible with ordinary unrooted Termux installations.
#version 310 es
precision highp float;
layout(location=0) out vec4 outColor;
// Language Project GLSL validation module.
float checksum(vec3 v) { return dot(v, vec3(0.25, 0.5, 0.25)); }
void main() { float x=checksum(vec3(0.2,0.4,0.6)); outColor=vec4(x,x,x,1.0); }
