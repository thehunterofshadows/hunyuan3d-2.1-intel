"""Backend policy tests: no accelerator or model downloads required."""
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backend
import torch


class IntelBackendTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {}, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def detect(self, **kwargs):
        with patch.object(torch.xpu, "is_available", return_value=True), \
             patch.object(torch.xpu, "device_count", return_value=2), \
             patch.object(torch.xpu, "get_device_name", return_value="B70"):
            return backend.detect(force_kind="xpu", **kwargs)

    def test_selected_device_and_precision(self):
        b = self.detect(force_device="xpu:1")
        self.assertEqual(b.device, "xpu:1")
        self.assertEqual(b.dtype, torch.float16)
        self.assertTrue(b.is_gpu and b.autocast_ok and b.needs_device_patches)
        self.assertFalse(b.is_cuda_like)

    def test_unavailable_explicit_device_is_error(self):
        with patch.object(torch.xpu, "is_available", return_value=False):
            with self.assertRaises(RuntimeError):
                backend.detect(force_kind="xpu")
        with self.assertRaises(ValueError):
            self.detect(force_device="xpu:2")
        with self.assertRaises(ValueError):
            self.detect(force_device="cuda:0")

    def test_cpu_raster_build_does_not_force_cpu_on_intel(self):
        with patch.object(backend, "_extension_raster_capability", return_value="cpu"):
            self.assertEqual(self.detect().raster, "torch")

    def test_memory_uses_selected_card_and_never_host_ram(self):
        b = self.detect(force_device="xpu:1")
        with patch.object(torch.xpu, "get_device_properties", return_value=SimpleNamespace(total_memory=32 << 30)) as p:
            self.assertEqual(backend.gpu_memory_gb(b), 32)
            p.assert_called_once_with("xpu:1")
        with patch.object(torch.xpu, "get_device_properties", side_effect=RuntimeError):
            self.assertIsNone(backend.gpu_memory_gb(b))

    def test_conservative_preset(self):
        self.assertEqual(backend.suggest_paint_preset(self.detect()), "safe")


if __name__ == "__main__":
    unittest.main()
