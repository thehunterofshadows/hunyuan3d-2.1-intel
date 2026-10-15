#!/usr/bin/env python3
"""Bounded, model-free Intel tests. Not an end-to-end Hunyuan benchmark."""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backend
import torch
import torch.nn.functional as F


def run(device):
    b = backend.detect(force_kind="xpu", force_device=device)
    backend.activate(b)
    torch.set_num_threads(4)
    report = {"scope": "model-free bounded operator probes", "torch": torch.__version__,
              "backend": backend.describe(b), "before": backend.memory_snapshot(b), "checks": []}
    if report["before"].get("free_bytes") is not None and report["before"]["free_bytes"] < 2 << 30:
        raise RuntimeError("Less than 2 GiB free; refusing even bounded probes")
    for dtype in (torch.float32, torch.float16, torch.bfloat16):
        a = torch.ones((256, 256), device=b.device, dtype=dtype)
        with torch.inference_mode():
            out = a @ a
        assert torch.equal(out, torch.full_like(out, 256))
        report["checks"].append({"op": "matmul", "dtype": str(dtype), "pass": True})
    # A small reference fits on CPU even if the GPU chooses dense math.
    torch.manual_seed(1234)
    q, k, v = [torch.randn(1, 4, 128, 64) for _ in range(3)]
    reference = F.scaled_dot_product_attention(q, k, v)
    for dtype in (torch.float16, torch.bfloat16):
        inputs = [x.to(device=b.device, dtype=dtype) for x in (q, k, v)]
        for _ in range(2):
            F.scaled_dot_product_attention(*inputs)
        backend.synchronize(b)
        t0 = time.perf_counter()
        out = F.scaled_dot_product_attention(*inputs)
        backend.synchronize(b)
        elapsed = (time.perf_counter() - t0) * 1000
        error = (out.float().cpu() - reference).abs().max().item()
        tolerance = 0.01 if dtype == torch.bfloat16 else 0.002
        assert error < tolerance, (dtype, error)
        report["checks"].append({"op": "sdpa_small", "dtype": str(dtype), "max_abs_error": error,
                                 "tolerance": tolerance, "elapsed_ms": elapsed, "pass": True})
    # Packed rasterizer tokens require int64 minimum reduction, not just FP ops.
    z = torch.full((4,), (2**31 - 1)**2, dtype=torch.int64, device=b.device)
    idx = torch.tensor([0, 0, 2], device=b.device)
    tokens = torch.tensor([2**40 + 7, 2**40 + 3, 17], dtype=torch.int64, device=b.device)
    z.scatter_reduce_(0, idx, tokens, reduce="amin")
    assert z.cpu().tolist() == [2**40 + 3, (2**31 - 1)**2, 17, (2**31 - 1)**2]
    report["checks"].append({"op": "int64_scatter_amin", "pass": True})
    # Observe selected small-workload kernels without claiming full-model coverage.
    try:
        with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,
                                               torch.profiler.ProfilerActivity.XPU]) as prof:
            F.scaled_dot_product_attention(*inputs)
            backend.synchronize(b)
        report["attention_trace"] = [e.key for e in prof.key_averages()
                                     if any(s in e.key.lower() for s in ("attention", "sdpa", "onednn", "flash"))]
    except Exception as exc:
        report["profiling_unavailable"] = type(exc).__name__ + ": " + str(exc)
    backend.synchronize(b)
    report["after"] = backend.memory_snapshot(b)
    report["status"] = "passed_operator_probes_only"
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="xpu:0")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run(args.device)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
