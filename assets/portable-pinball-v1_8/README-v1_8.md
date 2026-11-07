# Portable pinball cabinet — Prototype V1.8

V1.8 changes only three of the 45 enclosure parts: `left_front_wall`, `right_front_wall`, and `rear_vent_panel`. All earlier versions remain separate. Dimensions are millimetres.

## Control layout

Both nudge cutouts are on the same horizontal line as the flipper: Z = 30. The original flipper centre remains Y = 103; the nudge centre is Y = 136, giving **33 mm centre spacing**. The nudge opening is a plain **14.1 mm square** in the original flat exterior wall, without an external holder, bezel, pod, or mounting screws.

Each nudge opening has an inside **16.6 × 16.6 mm relief**, leaving a **1.5 mm snap-in plate** at the exterior. These dimensions assume an MX-style keyboard switch because the actual spare switch has not been measured. The 14.0, 14.1, and 14.2 mm coupons let the physical switch determine the final fit. Check clip engagement, orientation, travel, and access for wires; a modeled clearance does not prove a specific switch fits.

The two front flipper bores stay Ø28. Each now has an internal tapered reinforcement: **46 mm root diameter**, **44 mm flat bearing face diameter**, and **8 mm total local panel thickness**. The wall outside remains planar and the surrounding wall stays 4 mm thick. The root clears the 4 mm floor by 3 mm. At 33 mm centre spacing, the nominal gap between the collar and switch relief is 1.7 mm; the actual round and square through-openings have 11.95 mm of wall between them.

The collar's nut bearing face is flat. The new 8 mm local thickness needs enough threaded barrel length on the real flipper button. Confirm full nut engagement using the combined sample before printing whole walls.

## Rear grille and fan layout

The original rear panel envelope, wall thickness, and cabinet screw axes remain. An integrated spiral grille has eight broad curved spokes, a central hub, and a continuous rim, all within the original 4 mm wall thickness. There are no interior bosses consuming fan depth. The slot boundaries use smooth splines and circular ends. Nominal spoke arc width is 5 mm; the minimum sampled width normal to the curved spoke is approximately 4 mm.

The fan is a **nonprinted reference**: 120 × 120 × 25 mm, centred at X = 136 / Z = 88, with a 105 × 105 mm mounting pattern and four Ø4.5 mm through-holes. The mounting face is Y = 466, and the 25 mm case extends inward to Y = 441. A separate 27 mm installed-depth allowance is also checked. The reference case does not add an enclosure STL or change the 45-part count.

The original **60 × 25 mm cable opening** is retained in size and moved to X = 10…70 / Z = 50…75, left of the fan. It clears the corner bracket regions and leaves a 6 mm lateral gap to the assumed fan case. The fan is offset 6 mm right of the cabinet centre, retaining more access on the left below the hatch.

The 25 mm fan allowance has an 11 mm Y gap to the existing PC envelope and approximately 5.76 mm minimum vertical gap below the rear deck. With a 27 mm installed depth those become 9 mm and approximately 5.41 mm. These are modeled clearances. Actual fan blade/grille separation, connectors, cable bend radii, airflow, noise and cooling still need a physical check.

## Print first

1. Print `exports/print_first_tests/flipper_nudge_wall_sample.stl`. It is an exact section of the new left wall and tests the full control arrangement together. Fit the actual flipper barrel/nut, nudge switch, and wiring.
2. Print the `nudge_mx_14p0`, `nudge_mx_14p1`, and `nudge_mx_14p2` coupons. All include the same 16.6 mm inside relief and 1.5 mm snap plate. Choose based on the actual switch and printed dimensions.
3. The full front walls and combined sample are oriented **outer face down**; the reinforcement and relieved inside face print upward. The right wall uses the existing side orientation; the left front wall uses a new -90° Y rotation so its collar does not hold the rest of the wall off the bed.
4. Existing button, monitor, seam, and hatch coupons remain available. The tests directory contains 16 separate samples; these are not included in the 45 enclosure part count.

All enclosure STLs retain an 8 mm brim allowance on a 325 × 325 × 315 mm printer. Do not interpret the digital checks as physical assembly validation.

## Explicit hardware allowances

V1.7 reserved a generic 40 × 40 mm box immediately behind each 4 mm side wall. V1.8 intentionally adds reinforcement into the first 4 mm of that box. Instead of suppressing the conflict, the checker now uses explicit, documented assumptions: a Ø27.8 mm barrel in the Ø28 bore; a Ø40 × 5 mm nut starting 0.2 mm behind the new 8 mm face; and a 40 × 40 mm rear body/wiring allowance extending to the original 49.2 mm inward limit. These envelopes are checked against every printed part.

The nudge check uses a 14.0 mm plate stem and a 16.4 × 16.4 mm body/clip/wiring allowance, extending 20 mm inward from the exterior. The default plate opening provides 0.05 mm nominal clearance per side; the inside relief provides 0.1 mm per side to the assumed body. These are fit-test assumptions, not switch specifications. The monitor, cover, PC, encoder and front-button allowances continue to be checked.

## Build and validation

Use the existing CAD virtual environment:

```sh
../.venv/bin/python build_cabinet.py
../.venv/bin/python validate_meshes.py
```

`build_cabinet.py` creates the STEP assembly, print-oriented enclosure and sample STLs, inventory, manifest, and assembly-position meshes. It verifies valid single-solid parts and printer bounds, checks all printed pairs and all reserved hardware spaces, and measures the resulting CAD solids with volume probes.

The outputs include `geometry_checks.json`, `v1_8_feature_checks.json`, and `stl_mesh_checks.json`. The V1.8 report checks the 8 mm collar thickness, original 4 mm surrounding wall, 1.5 mm switch lip, open bores and reliefs, flat original exterior, fan mounting bores, cable opening, and grille material/openings. It records the actual modeled open area and hardware clearances. Any failed feature or unintended interference stops the build.

The `preview_meshes.json` file contains only the 45 printable enclosure parts. STEP includes clearly named nonprinted hardware/reference envelopes for review. Switches, keycaps and fans are not fabricated objects.

## Preserved V1.7 details

The other 42 printed enclosure parts are unchanged, including the lift-off two-peg hatch, corner nut slots, reinforced splices, monitor supports and their right-side height offset, bezels, lid, floor panels, and all fastening blocks. Keep using the monitor and seam fit tests as documented by the earlier prototype. No source or outputs in an older version are overwritten.
