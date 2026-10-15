#!/usr/bin/env bash
# Host-coupled diagnostics only: borrows an existing XPU Python environment read-only.
# Does not install or change host packages. See docs/intel/README.md.
set -euo pipefail
: "${XPU_VENV:?Set XPU_VENV to an existing Python environment with torch XPU}"
: "${PYTHON_RUNTIME_ROOT:?Set PYTHON_RUNTIME_ROOT to the directory containing its base Python}"
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
test_device="${HY3D_DEVICE:-xpu:0}"
mkdir -p "$project_dir/.build"
docker run --rm --network none --memory 4g --cpus 4 \
  --user "$(id -u):$(id -g)" --group-add "$(stat -c %g /dev/dri/renderD128)" \
  --device /dev/dri \
  -v "$XPU_VENV:/opt/venv:ro" \
  -v "$PYTHON_RUNTIME_ROOT:$PYTHON_RUNTIME_ROOT:ro" \
  -v /usr/lib/x86_64-linux-gnu:/hostlibs:ro \
  -v /usr/lib/x86_64-linux-gnu/intel-opencl:/usr/lib/x86_64-linux-gnu/intel-opencl:ro \
  -v /etc/OpenCL/vendors:/etc/OpenCL/vendors:ro \
  -v "$project_dir:/work" -w /work \
  -e LD_LIBRARY_PATH=/opt/venv/lib:/hostlibs \
  -e PYTHONDONTWRITEBYTECODE=1 -e OMP_NUM_THREADS=4 \
  -e HY3D_BACKEND=xpu -e HY3D_DEVICE="$test_device" \
  ubuntu@sha256:f144425ff09be612d6d9ad965196e9cdc23dae1f42110a8a11a3e9a8198759f7 \
  /opt/venv/bin/python "$@"
