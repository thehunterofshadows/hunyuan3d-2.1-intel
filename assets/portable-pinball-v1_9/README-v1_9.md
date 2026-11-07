# Portable pinball cabinet — Prototype V1.9

V1.9 extends the flipper reinforcement down to the bottom edge of both front side walls to reduce local wall flex. Exactly three of the 45 enclosure parts change from V1.8: `left_front_wall`, `right_front_wall`, and `bottom_front`. The other 42 parts, including the rear fan panel, are retained. Earlier versions remain separate. Dimensions are millimetres.

## Flipper reinforcement to the base

The reinforcement is a broad **D-shaped pedestal** on the inside of each front wall. It retains the V1.8 upper circular collar and continues its lower half straight down to **Z = 0**, the original bottom plane of the wall.

- **46 mm nominal width at the root**, tapering to a **44 mm wide flat inside face**.
- **8 mm total local wall thickness**, including the original 4 mm wall.
- The upper collar keeps its 23 mm root radius and 22 mm inside-face radius.
- The flipper remains **Ø28**, centred at **Y = 103 / Z = 30**.
- Both exterior faces remain planar. All existing wall screw holes remain in their original positions.

The continuous added thickness is intended to reduce bending of the wall beneath the button. Actual stiffness has not been physically tested. Button retention, cabinet joints, and how the assembled cabinet is supported can also affect the feel.

The flat bearing face and 8 mm mounting thickness are unchanged from V1.8. Confirm the actual flipper barrel has enough thread for its retaining nut.

## Matching front-floor relief

Use the **V1.9 front floor** with the V1.9 front walls. The full-height pedestals occupy space inside the original floor outline, so `bottom_front` now has two small edge notches:

| Side | X bounds | Y bounds | Depth |
|---|---|---|---|
| Left | 4.3…8.3 | 79.7…126.3 | Through the 4 mm floor |
| Right | 251.7…255.7 | 79.7…126.3 | Through the 4 mm floor |

Each notch removes only **4 mm of the floor edge** over a **46.6 mm length**. The floor remains **243.4 mm wide** between the notches. The new inside pedestal face has **0.3 mm nominal clearance** from the adjacent floor edge; the taper has at least that clearance from the rectangular notch.

The four front-floor mounting holes and all floor support blocks are unchanged. V1.9 uses the existing cabinet hardware; it adds no fasteners, brackets, or enclosure pieces. The unnotched V1.8 front floor overlaps the new pedestal and cannot be installed unchanged.

## Control layout retained from V1.8

Both nudge cutouts remain level with their flippers at **Z = 30**. The nudge centre is **Y = 136**, giving **33 mm centre spacing** rearward from the flipper. The exterior opening remains a plain **14.1 mm square**, with an inside **16.6 × 16.6 mm relief** leaving a **1.5 mm snap-in plate**. The external surface has no holder, bezel, pod, or switch mounting screws.

These dimensions assume an MX-style keyboard switch because the actual spare switch has not been measured. Use the 14.0, 14.1, and 14.2 mm coupons to check the physical switch's clips, orientation, seating, travel, and wiring. The nominal web between the reinforcement and inside switch relief remains 1.7 mm; the actual round and square through-openings have 11.95 mm of wall between them.

## Print first

1. Print `exports/print_first_tests/flipper_nudge_wall_sample.stl`. It is an exact section of the new left wall, including the full pedestal down to the bottom edge. Fit the actual flipper barrel/nut, nudge switch, and wiring.
2. Print `exports/print_first_tests/flipper_floor_notch_sample.stl`. It is the adjoining 20 × 78 × 4 mm floor section with the actual edge notch. Check the two samples in assembly orientation with their bottom faces coplanar and the floor perpendicular to the wall.
3. Both full front walls and the combined wall sample are oriented **outer face down**, with the inside reinforcement and switch relief upward. The floor and floor sample print flat. Keep those exported orientations.
4. The three `nudge_mx_14p*` coupons and the inherited button, monitor, seam, and hatch coupons remain available. There are **17 separate fit samples**, in addition to the 45 enclosure STLs.

The combined wall sample covers assembly Y = 76…154 / Z = 0…57. The adjoining floor sample covers X = 4.3…24.3 / Y = 76…154 / Z = 0…4 before its notch. Their STL files are independently moved onto the print bed; use their geometry when checking assembly fit.

All enclosure parts retain an 8 mm brim allowance on a 325 × 325 × 315 mm printer.

## Rear fan panel retained from V1.8

The rear panel still has eight curved grille spokes, a central hub, and a continuous rim within the original 4 mm wall thickness. The modeled fan case is **120 × 120 × 25 mm**, centred at X = 136 / Z = 88, with **105 × 105 mm** screw spacing and four Ø4.5 through-holes. A 27 mm installed-depth allowance is also checked. Fans and other hardware are reference envelopes and have no enclosure STLs.

The separate **60 × 25 mm** cable opening remains at X = 10…70 / Z = 50…75, with a 6 mm lateral gap to the assumed fan case. The 25 mm case has 11 mm Y clearance to the PC envelope; the 27 mm allowance leaves 9 mm. V1.9 leaves the entire rear fan panel unchanged.

## Hardware assumptions

The flipper checks retain V1.8's explicit allowances: a Ø27.8 barrel in the Ø28 bore; a Ø40 × 5 mm retaining nut starting 0.2 mm behind the 8 mm inside face; and a 40 × 40 mm rear body/wiring allowance extending to 49.2 mm inward from the exterior.

The switch check uses a 14.0 mm plate stem and a 16.4 × 16.4 mm body/clip/wiring allowance extending 20 mm inward. These allowances, the fan cases, monitor/cover, PC, encoder, and front controls are checked against every printed part.

Actual switch fit, threaded engagement, wiring, fan blade/grille spacing, cooling, and print strength remain physical checks. No modeled reserve establishes a particular unmeasured component's fit.

## Build and validation

Use Python with the packages in `requirements.txt` installed, including CadQuery 2.7:

```sh
python build_cabinet.py
python validate_meshes.py
python render_v1_9_details.py
```

The builder creates the STEP assembly, 45 print-oriented enclosure STLs, 17 sample STLs, inventory, manifest, and assembly-position meshes. It verifies valid single-solid parts, printer bounds, printed-part interference, and reserved hardware clearances.

The output reports are `geometry_checks.json`, `v1_9_feature_checks.json`, and `stl_mesh_checks.json`. The exact feature checks measure the full-thickness pedestal near Z = 0, its added bottom-face area, the preserved upper collar, all front-wall screw passages, the floor-notch removed volume, actual 0.3 mm floor clearance, floor mounting holes, control cutouts and reliefs, exterior planes, and the retained fan geometry. Any failed feature or unintended interference stops the build.

The `preview_meshes.json` file contains only the 45 printable enclosure parts. STEP includes clearly named nonprinted hardware/reference envelopes. Digital checks establish modeled geometry and exported mesh integrity; the assembled feel still needs a physical check.

## Retained parts

All other 42 enclosure parts match V1.8, including the rear fan panel, rear side walls, rear floor, two-peg lift-off hatch, corner brackets, reinforced seam splices, monitor supports, bezels, covers, and all fastening blocks. V1.8 source and output files are preserved.
