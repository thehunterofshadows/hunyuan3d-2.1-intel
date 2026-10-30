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
The Portable Pinball card uses exact tessellations of the supplied cabinet CAD: 46 named printable parts (V1.2; the right bezel is merged) and three explicitly marked reference envelopes. Assembly controls separate parts, hide top panels, toggle monitor/PC/cover references and isolate a named part. Download links preserve the original STEP assembly and CAD/STL print pack. No inference is used for the cabinet. It is a prototype; physical fit checks remain pending.

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
Left-click a mesh to select and highlight it without opening a window. Touch users can tap to open the inspector. Right-click the already selected mesh to reopen its notes/visibility panel. Center on Object moves the orbit pivot to that mesh while preserving angle and zoom. Use Unhide Objects in the top toolbar to restore manually hidden meshes; Reset Camera returns to the default fitted view. Empty-space right-click no longer opens a menu. Notes autosave after typing, with a browser draft if the service is unavailable. Each browser has a private cookie workspace; export JSON to share notes across devices or with an agent. Clearing cookies loses browser access to that workspace.

The notes service persists JSON plus readable Markdown in `/home/justin/.local/state/intel3d/part-notes`. Agents on Mini can read `README.md` and `workspace-*.json` there. Records identify model ID/asset path, CAD part name or mesh node path, geometry SHA-256, clicked coordinates, camera and visibility state, revision and timestamp. Use JSON as authoritative data. Local STL files stay in the browser; metadata alone does not supply their geometry.

Before first deployment, create the notes directory owned by UID 1000, mode 700. Build both Docker images and use `docker compose -f viewer/compose.yml up -d --no-build`. The API has same-origin writes and per-note revision checks. No notes or workspace cookies are logged. Back up the data directory separately from source.

Annotation checks: `viewer/tests/notes-api.py` exercises an isolated service (set `NOTES_TEST_URL`). `viewer/tests/part-notes.cjs` exercises browser selection, autosave, revisions, exports, transparency and desktop/touch restoration against a test deployment (`VIEWER_URL`). `viewer/tests/part-notes-public.cjs` is a production smoke check that never posts annotations. Run browser scripts in the existing Playwright Docker image; use a separate notes-data directory for test deployments.

## Portable pinball CAD V1.1
Source: `viewer/cad/portable-pinball-v1_1/`. Only the four `monitor_saddle_*` solids change from V1: 3 → 6 mm locator lips toward the outside, external triangular root braces, and 4 mm extra material below the bearing shelves. The monitor-facing stop planes, padded shelf elevations, bolt centers, and all other parts are unchanged. STLs print on an end face so layers include the full shelf/lip profile.

The active model keeps ID `portable-pinball` and the same CAD part names, preserving annotations. Existing notes on revised geometry show a fingerprint warning. Versioned `cabinet-v1_1.glb`, STEP, print-pack ZIP, preview and single-support test STL avoid stale cached models; V1 assets remain available. The ZIP contains matching source, 47 part STLs, 10 tests/shims and validation reports. Geometry has passed solid, interference, build-volume and STL manifold checks; physical fit and strength tests are pending. `viewer/tests/pinball-v1_1.cjs` checks the exact four-part geometry change and annotation compatibility without writing notes.

## Ultra Railgun (2026-10-16)
`#trellis-railgun-ultra` loads the new original 1536-resolution TRELLIS.2 GLB from Skynet. 24 steps, seed 42, 4096px texture atlas, 287,762 triangles. `assets/trellis-railgun-ultra/` preserves its concept reference, actual-model browser preview, manifest and original GLB. The download SHA256 matches Skynet. High-detail source; Instagib optimization/integration remains pending. `viewer/tests/ultra-railgun.cjs` verifies loading, triangle count, original download hash, clay display and mobile overflow.

### Pixal3D 1536 railgun (2026-10-16)
`#pixal3d-railgun` opens the actual Pixal3D textured GLB generated from Skynet's original railgun input. The generator is the *existing* trellis.cpp v0.8.1 Vulkan binary running the Pixal3D fine-tuned flows; no new inference service is published. 1536 geometry, 12 sampler steps, seed 42, horizontal FOV 49.13°, 2048px PBR atlas. Measured: 487.1 seconds end to end and 7,863.88 MiB peak Intel B70 GPU0 memory. Export: 21,066,352 bytes, 283,266 triangles, one mesh, one material, two embedded images, UV-textured GLB v2. The original binary in `assets/pixal3d-railgun/railgun.glb` is SHA256 checked against Skynet; `preview.png` is a Playwright screenshot from the real viewer canvas, not a concept image. `viewer/tests/pixal3d.cjs` verifies real WebGL loading, triangles, GLB download and mobile layout. This is an experimental high-poly model that is not optimized for Instagib.

### Ultra Railgun · Pixal3D (2026-10-16)
`#pixal3d-railgun-ultra` loads a verified, actual Pixal3D 1536-resolution GLB generated from the **same detailed reference** used for the TRELLIS.2 Ultra model. Inference used `trellis.cpp` v0.8.1 Vulkan on one Intel B70, seed 42, 24 sampling steps, 49.13-degree input horizontal FOV, and 4096px PBR atlas. Measured end-to-end generation was 1005.4 seconds and maximum GPU0 memory was 7888.883 MiB. Result: 277,166 triangles, 40,180,960-byte GLB with PBR textures, SHA256 `4bec5a119c12eace32828aef7298e43d981164192b9ca8e35b77e8546e4a9184`. `assets/pixal3d-railgun-ultra/manifest.json` records the provenance and full checksum. Its thumbnail is a Playwright/WebGL screenshot of the actual downloaded GLB. `viewer/tests/pixal3d-ultra.cjs` verifies browser loading, original GLB downloads and mobile layout. This is a high-poly concept reconstruction, not a game-ready Instagib mesh.

### Project folder browser (2026-10-16)
The model sidebar groups the 16 assets into **Instagib (8)** and **Pinball (8)** collapsible folders. Only the folder containing the current deep-linked model is open by default. The search box filters models by name/type/ID/project, expands matches temporarily and restores manually expanded/collapsed folder state when cleared. New entries without a folder are displayed under **Other** rather than silently omitted.

Folder membership is lightweight `folder` metadata in `viewer/site/app.js`; **do not move or rename existing `assets/` files, model IDs, or `/models/{id}/...` paths**. Existing bookmarked `#model-id` deep links (including same-tab hash navigation), downloads, local STL loading, part notes, and model-derived annotation IDs remain valid. Add `folder:'pinball'` or `folder:'instagib'` when adding models. Check via `viewer/tests/folders.cjs` plus `viewer/tests/browser.cjs`.

### Model modified dates and sort (2026-10-17)
Each model card and the details pane show the GLB file's HTTP `Last-Modified` timestamp (in the viewer's local timezone). Lightweight same-origin HEAD requests read timestamps without downloading the meshes again. The default sort is **Modified: newest first**, inside each project folder; users can select oldest first, name A–Z, or the original catalog order. Search, collapsed folder state, model IDs, downloads and notes remain unchanged.

The portable-pinball V1.1 CAD GLB intentionally has a reproducible UNIX-epoch file mtime, so its known Git release revision timestamp (`2026-10-16T20:42:03Z`) is used instead of misleadingly displaying 1970. Future reproducible/epoch-dated assets should specify a `modifiedFallback` based on their asset revision. If an asset supplies no usable date, the UI displays "Modified date unavailable" and sorts it last for date sorting. Verify using `viewer/tests/modified-date-sort.cjs`.

## Reviewing object notes
`reviewed` defaults to false (including legacy notes without the field). The editor shows only the pending text. Reviewed text and the agent's response appear in the history table below. Saving a new note archives the previous reviewed record with its object metadata; existing history is retained. Open inspectors refresh review status every five seconds while no local edits are pending.

Agents read `/home/justin/.local/state/intel3d/part-notes/workspace-*.json`, identify the exact model/part and revision, review the note, then run on Mini:
```sh
python3 viewer/notes/review_note.py --file /absolute/path/to/workspace-FULL_ID.json --model MODEL_ID --part PART_ID --expected-revision REVISION --response 'What was checked, changed, answered, or remains unresolved.'
```
Run from the repository root. Use the observed file and IDs; never guess. The script shares a file lock with browser saves, checks the revision, sets `reviewed: true`, records `reviewedAt`/`reviewResponse`, increments the revision, and updates JSON plus Markdown. A conflict requires re-reading and reviewing the new text. Do not manually overwrite live workspace files. Reviewed means examined, not necessarily fixed. Existing notes are not marked reviewed by deployment. Browser drafts and revision conflicts remain protected; use Reload saved note only when ready to discard the local draft.


### Yamaha VX110 wooden garage dolly (2026-10-26)
The `#vx110-wood-dolly` deep link is a manually modeled 93-part wooden rolling dolly (80 in padded bunk rails, 72×36 in 2x6 frame, 5 in casters, bracing and captive caster support bays). Built for preliminary transfer design for the 2005 Yamaha VX110 Sport. The nominal 21 in bunk height and 22 in bunk centers are placeholders pending exact trailer measurements and hull loading fit. It is not engineered or load certified. The viewer includes a source GLB and a downloadable/readable `BUILD_PLAN.md` with measured-cut instructions, line-item costs and winching precautions. Geometry is generated reproducibly with Python stdlib via `python3 viewer/tools/create_vx110_dolly.py`. Verify with `viewer/tests/vx110-dolly.cjs`.

## Portable pinball CAD V1.2 — A1 and A2 joined
The current `portable-pinball` model uses `cabinet-v1_2.glb` and the **same model ID**. The two right bezel parts `bezel_right_front` (A1) and `bezel_right_rear` (A2) are replaced by `bezel_right_a1_a2`, a single continuous printed rail. All other solids are inherited unchanged from V1.1; left bezel remains split. There are now 46 printable solids, plus 3 reference envelopes, and 10 tests/shims. The new right rail has unchanged 1 mm housing overlap and original screw locations (Y=140,330), and it is rotated 45° flat on the print bed to fit the QIDI X-Max 3 with an 8 mm per-side brim budget. The V1.1 files and annotations remain archived; old separate-part annotation IDs stay stored but do not correspond to a visible node in the new mesh. New versioned STEP, GLB, ZIP, preview and an individual merged-rail STL are served. Physical fit and printing remain unverified. Source and regeneration: `viewer/cad/portable-pinball-v1_2/`.

## Selected-part STL export
Select a mesh and use **Export selected STL** in the toolbar, or **Export this part STL** in its inspector. The cabinet's **Inspect part** dropdown also has an export button. Cabinet parts download the matching original V1.2 print STL, preserving millimeters and authored print orientation, independently of exploded views and visibility. Reference envelopes cannot be exported as printable parts. Other meshes export only the selected mesh as binary STL in millimeters, with authored node transforms, Z-up and its lowest point on Z=0; the viewer front rotation, centering and materials are excluded. Generated meshes retain their existing geometry and may need slicer repair/orientation. Verify via `viewer/tests/part-stl-export.cjs`.
