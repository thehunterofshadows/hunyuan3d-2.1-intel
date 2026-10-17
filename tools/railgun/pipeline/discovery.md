# Railgun pipeline verified discovery — 2026-10-17

Skynet: /home/justin/projects/trellis2-intel-lab (dev, d3fc634).
Pinned trellis.cpp v0.8.1 Docker Vulkan, B70 GPU 0/1. Weights in
/home/justin/ai/trellis2/models. Outputs in /home/justin/ai/trellis2/output.
Pixal3D multi-view is explicitly unsupported by the installed
upstream/docs/pixal3d/README.md (section on multi-view conditioning);
its current CLI accepts a single source image, not camera-calibrated views.
Do not invoke a fictitious multiview CLI or modify working model installs.

Mini: /home/justin/projects/hunyuan3d-2.1-intel (dev).
Viewer: viewer/site/app.js, viewer/Dockerfile, app container via viewer/compose.yml,
production https://3d.fireorbooty.com. Existing asset folders include
assets/pixal3d-railgun-ultra and assets/trellis-railgun-ultra.
Runs use installed intel3d-blender:railgun image (Blender 3.4.1).
Mini Instagib: /home/justin/projects/instagib, branch dev, see AGENTS.md.
First-person visual is src/client/rendering/railgun-view.ts;
game validation uses Docker, then dev sync with Skynet version verification.

Three real GLB candidates have been reimported and rendered by Blender.
Pixal 277166 -> 83149 triangles / 34MB; TRELLIS 287762 -> 86328
triangles / 41MB; original hard-surface 35116 triangles / 1MB.
The AI candidates still have ~4K original embedded PNGs even with geometry
decimated. Texture size reduction has not been verified by the initial
script, so don't call those fully optimized game assets.
Enhanced, hand-modeled V2: 47680 triangles / 2MB; real 3D output with
new heat pipes, fins, clips and cyan conduits; see assets/railgun-detail-v2.

ComfyUI on Skynet: /home/justin/ai/comfyui-ltx, largely LTX video
models plus a 9B image model. No installed verified geometry-conditioned
camera-locking image edit workflow or multi-view Pixal runtime was found.
Rather than silently downloading uncertain nodes/weights or independent
img2img hallucinations, keep Comfy enhancement explicitly unqualified.
Do not interrupt existing LLMs or deploy a different inference service.

Unverified: generation of true multi-view Pixal GLB, baked game textures,
M1 Mac performance and automatic camera-correct reconstructions.
