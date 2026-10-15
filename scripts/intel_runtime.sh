#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
: "${HY3D_RUNTIME:?Set the absolute directory of the prepared Intel test environment}"
: "${PYTHON_RUNTIME_ROOT:?Set the absolute directory containing the base Python}"
: "${UV_BINARY:?Set the absolute path to uv}"
docker run --rm --name "${HY3D_CONTAINER_NAME:-hy3d-intel-test}" --user "$(id -u):$(id -g)" --group-add "$(stat -c %g /dev/dri/renderD128)" --device /dev/dri --memory 64g --cpus 12 --shm-size 8g \
 -v "$HY3D_RUNTIME/models:/work/weights" \
 -v "$HY3D_RUNTIME:/runtime" \
 -v "$PYTHON_RUNTIME_ROOT:$PYTHON_RUNTIME_ROOT:ro" \
 -v "$UV_BINARY:/usr/local/bin/uv:ro" \
 -v /usr/lib/x86_64-linux-gnu:/hostlibs:ro \
 -v /usr/lib/x86_64-linux-gnu/intel-opencl:/usr/lib/x86_64-linux-gnu/intel-opencl:ro \
 -v /etc/OpenCL/vendors:/etc/OpenCL/vendors:ro \
 -v "$project_dir:/work" -w /work \
 -e HOME=/runtime -e UV_CACHE_DIR=/runtime/uv-cache -e HF_HOME=/runtime/hf \
 -e LD_LIBRARY_PATH=/runtime/venv/lib:/hostlibs -e PYTHONDONTWRITEBYTECODE=1 \
 -e HY3D_BACKEND=xpu -e HY3D_DEVICE="${HY3D_DEVICE:-xpu:0}" -e HY3D_RASTER=torch -e OMP_NUM_THREADS=8 \
 -e PATH=/runtime/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
 hy3d-intel-test:20261015 "$@"
