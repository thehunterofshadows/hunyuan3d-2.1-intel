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
