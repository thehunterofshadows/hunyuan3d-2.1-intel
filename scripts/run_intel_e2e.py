"""Run the existing visual E2E test with real XPU memory/timing telemetry."""
import atexit
import json
import runpy
import sys
import time
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
import backend
import torch
b = backend.detect(force_kind="xpu")
backend.activate(b)
torch.xpu.reset_peak_memory_stats(b.device)
started = time.perf_counter()
output = root / ".build" / "intel-e2e-memory.json"
def finish():
    report = backend.memory_snapshot(b)
    report.update(elapsed_seconds=time.perf_counter()-started, torch=torch.__version__)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+"\n")
    print("XPU telemetry:",json.dumps(report),flush=True)
atexit.register(finish)
runpy.run_path(str(root/"tests"/"e2e_visual.py"),run_name="__main__")
