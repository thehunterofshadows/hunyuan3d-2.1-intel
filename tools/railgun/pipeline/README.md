# Railgun asset pipeline

Runs in the existing Blender 3.4 Docker container; each invocation reimports the
exported real GLB and renders six fixed views. Source GLBs are never modified.

From repository root:

    bash tools/railgun/pipeline/run.sh pixal3d-railgun-ultra 0.3 512
    bash tools/railgun/pipeline/run.sh trellis-railgun-ultra 0.3 512
    bash tools/railgun/pipeline/run.sh railgun-built 1 512

Output: assets/railgun-pipeline/<source>-<ratio>/railgun.glb and evidence/.
Each manifest captures source/output hashes, triangle counts, material counts,
texture dimensions, Blender version and runtime. A decimated GLB is only a
candidate: visually verify its rails, pipes and first-person view before game use.

Installed Pixal3D trellis.cpp v0.8.1 expressly does not support multi-view
conditioning; multiple PNGs alone cannot establish a functional multi-view path.
ComfyUI is similarly unqualified until camera-preserving image conditioning has
actually been tested. Keep original asset and current game behavior intact.
