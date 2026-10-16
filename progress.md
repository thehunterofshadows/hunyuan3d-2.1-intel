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
