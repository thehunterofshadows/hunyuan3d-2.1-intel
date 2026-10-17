# Pixal3D railgun multiview demonstration

Actual textured output of four-image native Pixal3D inference on Skynet B70.
Source run: `/home/justin/ai/pixal3d-multiview/runs/railgun-mv-20261017-v2`.
Reproduce with `trellis2-intel-lab/multiview/run.sh` on Skynet.
Original reference and four generated inputs are preserved; see comparison.html.
No Blender, hand-built geometry, GLB-derived reference views or game optimization.

The 180.7 MB GLB is intentionally excluded from ordinary Git history. Canonical
copies remain on Skynet and Mini; restore it from the source run using SCP and
verify manifest.json's SHA256 before rebuilding the viewer. No LFS service or
paid asset storage was enabled. Small sources, gallery, validation and manifest
are tracked. Do not publish the model by substituting the input preview image.
