# Portable pinball cabinet — Prototype V1.10

V1.10 recesses the keyboard-switch mounting face **2.5 mm** into each front side wall and provides a separate **30 × 30 × 4 mm** switch-only fit sample. Exactly two of the 45 enclosure parts change from V1.9: `left_front_wall` and `right_front_wall`. The other 43 parts, including the notched front floor and rear fan panel, are retained. Dimensions are millimetres.

## Recessed nudge-switch opening

The switch remains centred at **Y = 136 / Z = 30**, level with the flipper and **33 mm rearward** from its centre. The ordinary wall remains 4 mm thick.

| Feature | Dimension |
|---|---:|
| Switch mounting-face setback from the original outside surface | 2.5 mm |
| Snap-in plate thickness behind that face | 1.5 mm |
| Default square aperture through the plate | 14.1 × 14.1 mm |
| Square well at the recessed mounting face | 18 × 18 mm |
| Square mouth at the outside surface | 23 × 23 mm |
| Taper between mouth and mounting face | 45° |
| Small standalone fit sample | 30 × 30 × 4 mm |

The broad tapered well lets the switch's upper housing enter the wall while preserving a flat seating surface around the square aperture. The 1.5 mm plate occupies inward depth 2.5…4 mm. Backside clip/body clearance begins at the original inside wall face, so no new inner boss or outside holder is added.

For the same switch and cap, fully seated in this new position, the axial setback would reduce outside projection by 2.5 mm. The actual switch and keycap have not been measured: the design does not establish an absolute finished button height, flushness, or full travel. Fit the actual switch and cap in the small sample and press the cap fully to check for contact with the rim.

The nominal solid gap between the outer well mouth and the flipper bore is **7.5 mm**. The gap between the smaller through-aperture and flipper bore remains **11.95 mm**. The cut stops before the flipper's internal reinforcement and nut bearing face.

## Print the small switch sample first

1. Print **`exports/print_first_tests/nudge_switch_fit.stl`**. This is the default 14.1 mm aperture in a small 30 × 30 × 4 mm blank, using exactly the same cut geometry as the wall. It omits the flipper hole and reinforcement.
2. Seat the actual keyboard switch from the recessed side. Check that both clips engage, the switch sits flat, and it cannot be pushed through.
3. Install the intended cap and press it through its full travel. Check that its underside and edges clear the surrounding wall, and that wiring remains accessible behind the plate.
4. If the printed aperture needs adjustment, the same recessed sample is available as `nudge_mx_14p0.stl` and `nudge_mx_14p2.stl`. The default sample replaces the former `nudge_mx_14p1` filename in this release; it is not an extra duplicate.

These dimensions retain the existing **MX-style switch assumption**. They are not a guarantee for an unmeasured switch variant. A successful test of the actual hardware is the fit criterion.

The samples and full walls are exported **outer face down**, so the wide recess mouth faces the bed and the internal reinforcement faces upward. Keep the same orientation and relevant slicer settings for the sample and wall. The tapered well is 45°, but the mounting face includes a **1.95 mm ledge on each side** of the aperture. That ledge may need tuned bridging or local support; support-free printing has not been physically verified. Inspect the sliced layers and printed clip edges before committing to the full walls.

## Flipper reinforcement and matching floor retained from V1.9

Each inside flipper reinforcement remains a broad D-shaped pedestal: **46 mm nominal root width**, **44 mm flat inside-face width**, and **8 mm total thickness**, continuing down to **Z = 0**. The upper circular collar, flat nut bearing area, original **Ø28** bore at **Y = 103 / Z = 30**, and wall screw axes are retained.

Use the existing **V1.9 notched front floor**, which is unchanged in V1.10. Its two edge notches run through the 4 mm floor at:

| Side | X bounds | Y bounds |
|---|---|---|
| Left | 4.3…8.3 | 79.7…126.3 |
| Right | 251.7…255.7 | 79.7…126.3 |

The full-height pedestal has **0.3 mm modeled clearance** from the floor. The unnotched V1.8 floor still overlaps the pedestal and is not a direct substitute. No additional fasteners, brackets, or enclosure pieces are required.

The combined `flipper_nudge_wall_sample.stl` includes the retained pedestal and the newly recessed switch opening. Its adjoining `flipper_floor_notch_sample.stl` is unchanged from V1.9. Those larger samples remain available when checking the whole control assembly and floor joint.

There are **17 separate fit samples** in addition to the **45 enclosure STLs**. All enclosure parts retain an 8 mm brim allowance on a 325 × 325 × 315 mm printer.

## Hardware clearance assumptions

The flipper allowances remain a Ø27.8 barrel, a Ø40 × 5 mm retaining nut starting 0.2 mm behind the 8 mm wall face, and a 40 × 40 mm rear body/wiring allowance extending to 49.2 mm inward from the outside.

The nudge's 14.0 mm plate-stem and 16.4 × 16.4 mm body/clip/wiring allowances are translated inward by **2.5 mm**. The body reserve now reaches **22.5 mm inward**. A separate 16.4 mm square upper-housing envelope checks that the assumed housing can enter the well and reach its mounting face. Its height is a clearance envelope, not a measured switch specification.

These switch and flipper allowances are checked against all printed parts and against the other control's allowances. Their minimum modeled separation is **4.8 mm** on each side. Components belonging to the same assumed switch intentionally overlap and are not treated as separate controls.

The monitor/cover, PC, encoder, front controls, and fan references continue to be checked. Actual hardware fit, cap travel, wiring, print strength, and assembled flipper feel remain physical checks.

## Rear fan panel retained

The V1.8/V1.9 rear panel is unchanged: eight curved grille spokes and a central hub within a 4 mm wall, four Ø4.5 mm mounting bores on a 105 mm square pattern, and a separate 60 × 25 mm cable opening. The 120 × 120 × 25 mm fan reference and 27 mm installed-depth allowance are still checked. Fans and other hardware are nonprinted reference envelopes.

## Build and validation

Use Python with the supplied requirements, including CadQuery 2.7:

```sh
python build_cabinet.py
python validate_meshes.py
python render_v1_10_details.py
```

The builder exports the STEP assembly, 45 print-oriented enclosure STLs, 17 sample STLs, inventory, manifest, and assembly-position meshes. It checks valid single-solid parts, printer bounds, printed-part overlap, reserved hardware spaces, and cross-control clearance.

Reports are `geometry_checks.json`, `v1_10_feature_checks.json`, and `stl_mesh_checks.json`. Exact CAD probes measure the actual recessed mounting face, 1.5 mm plate, 14.1 mm aperture, 18/23 mm well, taper, sample-to-wall correspondence, full retained flipper pedestal and nut bearing region, floor clearances, original screw passages, and the retained fan geometry. Failed features or unintended interference stop the build.

The preview mesh file contains only the 45 printable enclosure parts. STEP adds clearly named nonprinted hardware/reference envelopes. All earlier version source and outputs remain separate.
