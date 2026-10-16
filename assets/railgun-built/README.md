# Railgun — modeled rebuild

Created from the approved railgun reference using deterministic Blender hard-surface modeling. This is a real 3D asset, not an image-to-3D reconstruction or an imagegen render.

- 35,116 triangles; eight exported mesh/material groups.
- 189 individually editable authoring parts in railgun.blend.
- Beveled rails, receiver panels, coil braces, screws, trigger guard, grips and stock.
- Clean PBR metal/rubber materials with cyan emissive inserts; no baked AI texture atlas.
- Named Muzzle, RightHand and LeftHand attachment nodes.
- Approximate length 1.305 metres. glTF Y-up; barrel points negative X.
- No rig, animations, collider or live Instagib integration. No LODs yet.

The design follows the visible reference's main shapes, colors and features; it is an interpretation, not an exact reconstruction. Back and underside were designed consistently with the visible side. Preview is rendered directly from the GLB by Three.js. Viewer lighting can differ from game lighting; bloom is not embedded in the model.

Build from repository root:

```sh
docker build -t intel3d-blender:railgun tools/railgun
docker run --rm -u $(id -u):$(id -g) -e HOME=/tmp -v "$PWD:/work" intel3d-blender:railgun --python-exit-code 1 --python tools/railgun/build.py
```

Authoring file preserves individual parts/modifiers. Export applies modifiers and joins by material to reduce draw calls. The earlier generated railgun is preserved separately under assets/intel-railgun.
