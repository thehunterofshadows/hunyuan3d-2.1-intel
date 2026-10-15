"""Small real-GPU checks; run in a fresh process because patches are global."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backend
import torch
import compat_patches

b = backend.detect(force_kind="xpu")
assert compat_patches.apply(b)
assert compat_patches.apply(b)
x = torch.ones(32, 32, device=b.device)
with torch.autocast("cuda", dtype=torch.float16):
    y = x @ x
assert y.dtype == torch.float16 and y.device == torch.device(b.device)
with torch.autocast("cuda", enabled=False):
    assert (x @ x).dtype == torch.float32
with torch.autocast("xpu", dtype=torch.bfloat16):
    assert (x @ x).dtype == torch.bfloat16
start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
start.record()
y = x @ x
end.record()
torch.cuda.synchronize()
assert start.elapsed_time(end) >= 0
torch.cuda.empty_cache()
from dataclasses import replace
try:
    compat_patches.apply(replace(b, dtype=torch.float32))
except RuntimeError:
    pass
else:
    raise AssertionError("Must reject changing a globally patched worker")
print("PASS: XPU autocast, disabled autocast, BF16, real events, synchronization, cache, worker guard", b.device)
