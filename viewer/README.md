# Intel 3D Studio viewer

Production only: https://3d.fireorbooty.com/ on Mini. The owner explicitly requested no Dev site.
Source stays on the existing fork's dev branch. A built Docker image is deployed; there is no source bind mount and no inference service exposed.
This does not promote or change the upstream main branch.

## Features
Three.js 0.186.1 served locally (no CDN); six GLB models, including a modeled railgun rebuild and TRELLIS.2 railgun and bumper outputs; mouse/touch orbit, zoom and pan; camera presets, reset, fullscreen where supported; studio lighting; exposure; backgrounds; clay, normal and wireframe inspection; reference image and GLB download.
The original three models are unmodified experimental outputs. Railgun · rebuilt is a separately authored hard-surface asset with 35,116 triangles and eight material groups; its editable Blender source is included. Character has no skeleton/animations and significant texture defects. Original PBR maps are displayed honestly.

## Build and deploy
From repository root:
```sh
docker compose -f viewer/compose.yml -p intel-3d-studio build
docker compose -f viewer/compose.yml -p intel-3d-studio up -d
```
Internal origin: intel-3d-studio-prod-web:80 on existing edge network. GET /health returns ok. No host ports, GPU, credentials, uploads or model-generation endpoints.
The approved public hostname serves these already-public reference images and GLBs. Cloudflare configuration and private backups stay on Mini outside this repository.

## Browser verification
On Mini, using its existing Playwright 1.54 image:
```sh
docker run --rm --network edge -v "$PWD/viewer/tests:/tests:ro" -v /home/justin/.local/state/intel3d:/evidence pinball-integration-browser:playwright-1.54.0 node /tests/browser.cjs
```
Checks all three models/downloads, desktop rotation/zoom, inspection controls and mobile layout. The test uses software rendering, not an FPS benchmark.
Optional VIEWER_URL container environment selects a public deployment.

## Updating assets
Add asset under assets/, update Dockerfile COPY and models list in site/app.js, rebuild and verify. No inference runs automatically.
Before updates, tag the existing Docker image for rollback. To roll back, retag the saved image as intel-3d-studio:latest and run compose up -d --force-recreate --no-build.
No mutable user data exists; source/assets are backed by Git. No automatic watcher or AI Runner registration was requested as part of this viewer deployment.

### Bumper chrome preview
The TRELLIS bumper enables **Chrome polish** by default. This viewer-only shader
uses base-color saturation/brightness to approximate silver, red cap and rubber
regions, adjusts roughness/metalness, and uses the existing studio environment.
Turn the checkbox off to compare the untouched generated material. This is an
approximation, not semantic segmentation; small misclassified areas can remain.
The download is explicitly labeled **original GLB** and excludes this shader.
Other assets and geometry are unchanged. The bumper browser check compares actual
rendered pixels with polish on/off and captures all views.


### Portable pinball CAD
The Portable Pinball card uses exact tessellations of the supplied cabinet CAD: 47 named printable parts and three explicitly marked reference envelopes. Assembly controls separate parts, hide top panels, toggle monitor/PC/cover references and isolate a named part. Download links preserve the original STEP assembly and CAD/STL print pack. No inference is used for the cabinet. It is a prototype; physical fit checks remain pending.

Open STL file parses ASCII or binary STL locally using the bundled Three.js STLLoader, converts millimeters Z-up to the viewer's meter Y-up convention, and leaves the file in the browser. No upload endpoint is added. STEP is supplied as an editable download; the browser displays its preconverted GLB geometry.

The portable-pinball browser test verifies the actual part count, all view modes, explode/hide/isolation, local STL loading, downloads, rotation/zoom and mobile layout. Run it in the same Playwright image as the existing tests.

Regenerate the cabinet web asset from the extracted CAD pack:
```sh
python3 viewer/tools/export_pinball_glb.py --cad-dir /path/to/pinball_cad_v1 --output assets/portable-pinball --print-pack /path/to/pinball_cabinet_v1_print_pack.zip
```
The converter uses NumPy and preserves named parts and reference metadata.

### TRELLIS.2 pinball component collection (2026-10-16)
Five **actual GLB exports** from Skynet's trellis.cpp v0.8.1 image-to-3D Vulkan backend: flipper bat, plunger, slingshot, drop target, pop bumper. GPU0 and GPU1 ran simultaneous worker processes, one per B70. All five are 512 geometry resolution, seed 42, 12 inference steps, with 2048px PBR atlases; 140k–148k triangles each. Files and original illustrated inputs are stored under `assets/trellis-pinball-*`, with provenance and SHA256 in per-part READMEs. `viewer/tools/sync_pinball_trellis.py` syncs the outputs over SSH and registers the viewer.

The sidebar `preview.png` images are **screenshots of the actual GLBs** from Playwright/WebGL, not image generation mockups. Generated results are experimental: surfaces and colors are approximate, especially the slingshot and target; none are mechanically functional, optimized or print ready. The slingshot has unwanted bulky geometry. The target uses optional, viewer-only color correction; pop bumper offers optional chrome polish. Downloads remain the untouched exports. `viewer/tests/pinball-parts.cjs` loads all five, verifies geometry/downloads, captures previews, and checks mobile layout.


## Part annotations
Click a mesh to edit notes or set its opacity. Right-click empty canvas space (or use Hidden parts) to restore manually hidden meshes. Notes autosave after typing, with a browser draft if the service is unavailable. Each browser has a private cookie workspace; export JSON to share notes across devices or with an agent. Clearing cookies loses browser access to that workspace.

The notes service persists JSON plus readable Markdown in `/home/justin/.local/state/intel3d/part-notes`. Agents on Mini can read `README.md` and `workspace-*.json` there. Records identify model ID/asset path, CAD part name or mesh node path, geometry SHA-256, clicked coordinates, camera and visibility state, revision and timestamp. Use JSON as authoritative data. Local STL files stay in the browser; metadata alone does not supply their geometry.

Before first deployment, create the notes directory owned by UID 1000, mode 700. Build both Docker images and use `docker compose -f viewer/compose.yml up -d --no-build`. The API has same-origin writes and per-note revision checks. No notes or workspace cookies are logged. Back up the data directory separately from source.

Annotation checks: `viewer/tests/notes-api.py` exercises an isolated service (set `NOTES_TEST_URL`). `viewer/tests/part-notes.cjs` exercises browser selection, autosave, revisions, exports, transparency and desktop/touch restoration against a test deployment (`VIEWER_URL`). `viewer/tests/part-notes-public.cjs` is a production smoke check that never posts annotations. Run browser scripts in the existing Playwright Docker image; use a separate notes-data directory for test deployments.
