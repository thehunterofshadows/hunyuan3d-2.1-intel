#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/../../.."
name="${1:-pixal3d-railgun-ultra}"
ratio="${2:-0.3}"
size="${3:-512}"
case "$name" in pixal3d-railgun-ultra|trellis-railgun-ultra|railgun-built|railgun-hard-surface-v2) ;; *) echo "Bad source";exit 2;;esac
if [ "$name" = railgun-built ];then filename=railgun.glb;else filename=railgun-ultra.glb;fi
if [ "$name" = railgun-hard-surface-v2 ];then input="assets/railgun-pipeline/$name/railgun.glb"; else input="assets/$name/$filename";fi
id="$name-$(echo "$ratio"|tr . p)"
out="assets/railgun-pipeline/$id"
mkdir -p "$out/evidence"
docker run --rm --network none --user "$(id -u):$(id -g)" -v "$PWD:/work" -w /work intel3d-blender:railgun --python /work/tools/railgun/pipeline/blender_pipeline.py -- --input "/work/$input" --output "/work/$out/railgun.glb" --run-dir "/work/$out/evidence" --ratio "$ratio" --size "$size" 2>&1 | tee "$out/evidence/blender.log"
python3 tools/railgun/pipeline/validate.py "$out/evidence/manifest.json"
echo "OUTPUT=$out/railgun.glb"
