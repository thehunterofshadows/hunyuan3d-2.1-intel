# Initial validation, 2026-10-15

- Backend policy unittest: 5 passed.
- Operator probes: 6 checks on each of two Arc Pro B70 cards, all passed.
- Rasterizer reference: 7 CPU and 7 XPU:0 scene comparisons passed.
- Attention chunking: 9 XPU:0 checks passed, including masks and FP16.
- Compatibility smoke: XPU autocast, disabled autocast, BF16, real timing events,
  synchronization, cache handling and worker identity guard passed on both cards.

Probe JSON captures native small SDPA dispatch before compatibility patches.
The BF16 trace includes the fused overrideable attention operator and micro_sdpa.
These results do not establish production attention coverage or full model quality.
Profiler overhead and driver allocations are excluded from PyTorch allocation
counters; the sub-megabyte tensor peak is not total GPU process memory.
No model weights were downloaded and no existing GPU workload was stopped.
Reproduction and exact environment are in ../README.md.
