# Experimental Intel XPU port

This branch adds the first Intel backend foundation to the community Hunyuan3D
2.1 wrapper. It is not yet a validated image-to-textured-GLB installation.
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

## Remaining gates, in order

1. Build an independent, pinned application image including upstream dependencies;
   audit CUDA strings/device objects, captured SDPA aliases and import order.
2. With adequate free VRAM, generate shape from a fixed reference image. Compare
   mesh validity and geometry against the reference backend.
3. Qualify paint, RealESRGAN and complete textured GLB export. The new paint
   routes are code changes only, not yet runtime-validated model integration.
   FP16 is the initial pipeline precision; BF16 probes do not establish BF16
   support throughout upstream paint.
4. Profile real attention shapes, masks and dtypes. Enable native fused SDPA
   selectively only after memory/correctness validation; optimize rasterizer
   synchronization and batching based on measured bottlenecks.
5. Benchmark quality, stage latency and peak VRAM. Then evaluate per-GPU workers
   and model placement. Two 32 GB cards do not form a transparent 64 GB pool.

Do not stop unrelated workloads to run tests. The initial session found roughly
20.4 GiB already occupied on each card; full model qualification is pending.
Preserve upstream license files and notices. Resolve the wrapper-file coverage
discrepancy between NOTICE and LICENSE-WRAPPERS before distributing a packaged
release; model weights retain their own upstream license terms.
