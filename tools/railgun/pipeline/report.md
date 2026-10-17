# Railgun pipeline verified report — 2026-10-17

## Real model results
Original Pixal3D Ultra: 277166 -> 83149 triangles (0.30 ratio); 34.1MB result.
Original TRELLIS.2 Ultra: 287762 -> 86328 triangles (0.30 ratio); ~41.3MB result.
Original hard-surface: 35116 triangles, ~1MB.
Chosen hard-surface V2: 47680 triangles, 14 materials, ~2MB; copper pipes, radiator fins, energy conduits.
Game optimized candidate: 123 meshes reduced to 14 merged material meshes, same 47680 triangles.
All preview PNGs produced from re-imported actual GLB geometry; original images/GLBs preserved.

## Commands (from Mini viewer repo root)
bash tools/railgun/pipeline/run.sh pixal3d-railgun-ultra 0.3 320
bash tools/railgun/pipeline/run.sh trellis-railgun-ultra 0.3 320
bash tools/railgun/pipeline/run.sh railgun-built 1 320
bash tools/railgun/pipeline/run.sh railgun-hard-surface-v2 1 520
Generate V2 source using tools/railgun/pipeline/detail_blender.py and optimize_game.py.

## Verification
Manifest and actual-model renders under ignored assets/railgun-pipeline subfolders.
Viewer https://3d.fireorbooty.com/#railgun-detail-v2 deployed, health ok.
Viewer original Playwright browser suite passed; targeted test must be checked separately.
Game viewmodel available only using ?railgunModel=detail; default is original.
Game dev deployment, M1 and GamingPC WebGPU FPS must be tested before default promotion.

## Unsupported / not attempted
Pixal3D multiview is explicitly OUT OF SCOPE for pinned trellis.cpp v0.8.1; no real multiview inference claimed.
ComfyUI geometry-guided camera-locking not installed/qualified; no workflow run claimed.
AI input 4K PNG textures were not reduced by initial Blender decimation experiment.
Historical Skynet Pixal3D ultra benchmark: 1005.4 seconds, 7888.883 MiB max on GPU0.
Rollback: revert viewer model registration and Dockerfile then rebuild, previous original entries unchanged.
Previous viewer image rollback tagging failed because old image SHA was already pruned.
