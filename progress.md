# Intel port progress

2026-10-15: Created Intel fork and `dev` branch from community commit
`6f4b63bd6419406f40291bca23a7c849bcaae2a3`. Added native XPU backend foundation,
compatibility routing, model-free probes and Docker diagnostic harness.

See [Intel port notes](docs/intel/README.md) for scope, reproduction and remaining
gates. Full shape/paint model execution and performance qualification remain open.
Existing GPU workloads were preserved.
