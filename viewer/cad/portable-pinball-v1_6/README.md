# Portable Pinball CAD V1.6 — reinforced wall splices

Based on V1.5, which is preserved unchanged. Source: `build_cabinet.py` and `parameters.json`; regenerate with CadQuery 2.7.

## V1.6 changes

- **Left and right mid-wall splice plates:** increase thickness from 4 to **6 mm**, while retaining the 64 mm length along the wall (Y=203 to 267 mm). Extend vertically from Z=12–60 mm to **Z=12–95 mm** (height **83 mm**). The external cabinet dimensions and original splice-to-wall seating face are unchanged.
- **Fastening:** retain the original four holes on each wall at Y=215/255, Z=25/50; add an upper pair at Y=215/255, **Z=85 mm**. Six 3.4 mm through-holes per splice, matching each panel. Each splice therefore gains one additional screw above the seam on each wall section. Left/right positions are mirrored inward, avoiding intrusion into the exterior cabinet envelope.
- **Hardware:** suggested **M3 × 16 mm** machine screws with M3 hex nuts for the splice plates, rather than the old M3 × 12 mm. Verify actual screw engagement and washer stack; do not overtighten into PETG.
- **Sound exciters:** preserve **4 mm** rear side walls; no exciter holes or permanent stiffening. Trial adhesive/contact placement near the upper middle of each rear wall, clear of top blocks, saddle brackets and rear ventilation slots. The final mounting spots must be verified on the actual assembled cabinet for internal PC and cable clearance.
- **Unchanged:** monitor geometry, 5 mm right saddle rise, one-piece bezels, captive corner nuts, printer fit constraints, DMD/screen allowances, and rest of cabinet.

## Print-first test

Print `exports/print_first_tests/joint_front_wall.stl`, `joint_rear_wall.stl`, and `joint_splice_plate.stl` to test the six-hole fastening stack, wall seam geometry, hardware reach and rigidity. Check an M3 × 16 with intended washers and nuts for full engagement. Confirm no fit conflict with the monitor and cables before printing a complete set. Do not assume printed dimensions match nominal CAD perfectly.

## Exports

- `exports/mini_vpin_assembly.step`: full STEP assembly (includes clearance envelopes).
- `exports/enclosure_stl/*.stl`: separately oriented print parts.
- `exports/print_first_tests/*.stl`: assembly fit coupons.
- `exports/geometry_checks.json`, `stl_mesh_checks.json`, `parts_manifest.json`, `print_inventory.csv`: validation and part data.
- `exports/cad_preview.png`, `fit_test_preview.png`: CAD-derived images.

**Prototype only:** CAD validity and clearance do not replace physical fit tests or strength testing.
