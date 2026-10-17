# Intel port progress

2026-10-15: Created Intel fork and `dev` branch from community commit
`6f4b63bd6419406f40291bca23a7c849bcaae2a3`. Added native XPU backend foundation,
compatibility routing, model-free probes and Docker diagnostic harness.

See [Intel port notes](docs/intel/README.md) for scope, reproduction and remaining
gates. Full shape/paint model execution and performance qualification remain open.
Existing GPU workloads were preserved.

2026-10-15, full runtime validation:
- [x] Dedicated Docker test environment and independent Python dependencies.
- [x] Shape generation on B70, 30 steps and octree 192.
- [x] Safe-preset PBR generation, GLB export and four-view rendering.
- [x] Finite geometry/UV and embedded PBR material validation.
- [x] Recorded timings, allocation telemetry and visual evidence.
- [ ] Matched reference-backend comparison and game-quality visual acceptance.
- [ ] Higher-resolution presets, performance optimization and portable release image.

See docs/intel/e2e-2026-10-15/README.md for measured results and limitations.

## Production-only model viewer — 2026-10-16 UTC

- [x] Three.js gallery for bumper, railgun and woman; rotate/zoom/pan and inspection controls.
- [x] Docker deployment on Mini; approved hostname 3d.fireorbooty.com only.
- [x] Browser checks: all three GLBs, rotation/zoom, materials, mobile layout.
- [x] Shared Cloudflare route and DNS verified.
- [ ] Repair source assets and qualify game-ready character topology/rigging (separate work).

- [x] Fixed double-V GLB export conversion; repaired all three gallery GLBs; raw-accessor regression and browser visual checks passed.

## 2026-10-17 — native four-view Pixal3D railgun

Added `pixal3d-railgun-multiview` to the existing Instagib model folder, preserving
all previous assets. This is actual native ComfyUI Pixal3D multiview inference
on Skynet's B70, not a Blender/manual replacement: four generated camera views
from the unchanged ultra railgun PNG produced a raw textured GLB.

Output: 180,709,028 bytes, 6,463,700 triangles, two 2048px PNG PBR maps. SHA256
`a1a3be73f4b3bf63a3a392989d644401b0e14b1c192d857fab20f39688037c3e`. The large
GLB stays out of ordinary Git and is recoverable from the preserved Skynet run.
Original, four generated inputs, camera assumptions, manifest and actual-GLB
viewer screenshots are included in the comparison gallery. The viewport link
appears only for this model; existing models retain their reference behavior.

An isolated production-code Docker image loaded the actual GLB, validated its
header/triangle count, loaded the original plus all four images and rendered
front/back views without console errors (exit 0). This is not a hardware FPS
benchmark. Raw reconstruction fidelity is imperfect; no surface cleanup or
optimization was substituted. Pipeline commit `88eb450` in trellis2-intel-lab.

Final candidate image verification also passed the existing three-model,
desktop rotation/zoom, inspection-control and mobile-layout regression suite
(exit 0). A small desktop workspace rule prevents the long catalog from
pushing the actual model below the visible browser area. No model geometry
was changed for this display fix.
