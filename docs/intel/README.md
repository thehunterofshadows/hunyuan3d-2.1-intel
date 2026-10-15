# Experimental Intel XPU port

This branch adds the first Intel backend foundation to the community Hunyuan3D
2.1 wrapper. A first image-to-textured-GLB run passed on Arc Pro B70 at the safe preset.
See [results and previews](e2e-2026-10-15/README.md). This is an experimental
installation; game-quality output and cross-backend parity remain unqualified.
Upstream baseline: `6f4b63bd6419406f40291bca23a7c849bcaae2a3`.

## Implemented

- Native `xpu` detection, explicit `HY3D_DEVICE=xpu:0` or `xpu:1`, real per-card
  memory reporting, synchronization and cache management.
- CUDA autocast requests redirect to XPU autocast. Legacy event calls use real
  XPU events. A patched worker rejects backend/device/precision changes.
- Torch rasterizer selected by default on XPU. RealESRGAN device selection now
  targets XPU, and paint cache identity includes device and precision.
- Conservative paint preset and existing bounded attention fallback retained.
  Small fused-attention success does not qualify production multiview shapes.

## Diagnostics

`scripts/intel_diagnostics.sh` runs model-free tests in Docker with no network,
4 CPU cores and 4 GiB host RAM. It borrows a preexisting torch-XPU environment
and matching host drivers read-only. GPU memory is **not** capped by Docker's
host-memory limit; these probes use deliberately small tensors. It exposes both
cards but selects one per worker. This is a host-coupled diagnostic harness,
not the independently packaged application environment still to be built.

Validated host: Ubuntu 26.04, Python 3.12.14, torch 2.13.0+xpu, two Arc Pro B70
32 GB cards, Intel compute runtime 26.22.38646.7, Level Zero loader 1.28.6.
The container borrows Linux x86-64 libraries and is not a Windows installer.
Both Level Zero **and OpenCL** must be visible: without the OpenCL ICD mounts,
matmul worked but oneDNN SDPA failed with `could not create a primitive`.

Set absolute paths for your installed environment and the base Python directory
that its `bin/python` symlink targets, then run from the repository root:

```bash
export XPU_VENV=/absolute/path/to/existing/xpu-venv
export PYTHON_RUNTIME_ROOT=/absolute/path/containing/base-python
bash scripts/intel_diagnostics.sh tests/test_xpu_backend.py
HY3D_DEVICE=xpu:0 bash scripts/intel_diagnostics.sh scripts/probe_xpu.py --device xpu:0 --output .build/xpu0-probe.json
HY3D_DEVICE=xpu:1 bash scripts/intel_diagnostics.sh scripts/probe_xpu.py --device xpu:1 --output .build/xpu1-probe.json
bash scripts/intel_diagnostics.sh tests/test_xpu_compat.py
bash scripts/intel_diagnostics.sh tests/test_sdpa_chunking.py
bash scripts/intel_diagnostics.sh tests/test_torch_rasterizer.py
```

Run each compatibility test in a fresh process. Global upstream compatibility
patches are not designed for multiple simultaneous device backends in one process.
Recorded probe timings are individual tiny calls, not throughput benchmarks.

## Validation status and remaining gates

1. **Passed:** isolated application environment, model imports and native CPU
   inpainting extension. Packaging still depends on host GPU libraries.
2. **Passed on one example:** shape generation, safe-preset paint, RealESRGAN,
   textured GLB export, independent structural checks and four-view previews.
3. **Pending:** matched reference-backend comparison, PBR inspection in the game,
   broader input coverage and artifact diagnosis. FP16 is the initial pipeline
   precision; BF16 operator probes do not qualify BF16 throughout paint.
4. **Pending:** profile production attention shapes, masks and dtypes before
   enabling higher-resolution settings; optimize measured bottlenecks.
5. **Pending:** warmed latency/VRAM benchmarks, portable release image and
   per-GPU worker scheduling. Two cards do not create a transparent VRAM pool.

Do not stop unrelated workloads to run tests. The initial session found roughly
20.4 GiB already occupied on each card; the full test subsequently ran with that workload temporarily unloaded under
explicit user authorization. Quality qualification is still pending.
Preserve upstream license files and notices. Resolve the wrapper-file coverage
discrepancy between NOTICE and LICENSE-WRAPPERS before distributing a packaged
release; model weights retain their own upstream license terms.

## Full runtime test reproduction

The full test uses its own Python environment and model directory; it does not
borrow or modify the LLM environment. The container still mounts matching host
GPU libraries read-only, so it is not yet a portable release image.

```bash
docker build -t hy3d-intel-test:20261015 -f docker/intel-test.Dockerfile .
export HY3D_RUNTIME=/absolute/path/to/dedicated/runtime
export PYTHON_RUNTIME_ROOT=/absolute/path/containing/base-python
export UV_BINARY=/absolute/path/to/uv
mkdir -p "$HY3D_RUNTIME/models"
# Clone Tencent upstream into Hunyuan3D-2.1 and checkout the revision above.
# Create the venv inside Docker, using your actual base Python path:
bash scripts/intel_runtime.sh uv venv --seed --python /absolute/path/to/python3.12 /runtime/venv
bash scripts/intel_runtime.sh uv pip install --python /runtime/venv/bin/python torch==2.13.0+xpu torchvision==0.28.0+xpu --index-url https://download.pytorch.org/whl/xpu
bash scripts/intel_runtime.sh uv pip install --python /runtime/venv/bin/python -r requirements_rocm.txt
bash scripts/intel_runtime.sh python scripts/download_intel_test_models.py
bash scripts/intel_runtime.sh python scripts/build_extensions.py --raster torch
bash scripts/intel_runtime.sh python scripts/run_intel_e2e.py --tex-preset safe --raster torch --octree 192 --resolution 256
```

The tested dependency snapshot is in `requirements-tested.txt`. The commands above
resolve shared application dependencies; use the snapshot as constraints when
reproducing exact versions. Additional DINO and background-removal models download
on first use. Tests may consume significant GPU memory; arrange free capacity
before launching. The runtime script never stops existing services automatically.
