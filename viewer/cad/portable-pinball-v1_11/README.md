# Portable pinball cabinet — Prototype V1.11

V1.11 softens the exposed front corners of **both front side walls, the front button panel, and the front cable lid**. The treatment uses a short 45° bevel followed by a **1 mm curved blend**. Its maximum inward depth is **1.5 mm**; the lid's upper rim uses a smaller **1 mm** depth so the curved corner stays clean. A small corner test kit reproduces the actual wall, panel, lid, seams, and mounting geometry.

Exactly **four of the 45 enclosure parts** change from V1.10:

- `left_front_wall`
- `right_front_wall`
- `front_button_panel`
- `front_cable_lid`

The other **41 enclosure parts** are retained, including the V1.9 notched front floor, existing corner brackets and top blocks. The V1.10 recessed nudge opening, small switch test, and full-height flipper reinforcement remain.

## How the corners are softened

| Location | Inward treatment depth | Curved blend | Other geometry |
|---|---:|---:|---|
| Outer vertical front corner of each side wall | 1.5 mm into the wall | 1.0 mm radius | Initial 45° bevel; outside-face offset about 1.086 mm |
| Upper front edge shared by panel and side-wall ends | 1.5 mm in the front-to-back direction | 1.0 mm radius | Initial 45° print slope, then tangent to the existing 10° sloping top; front-face offset about 0.980 mm |
| Upper front and side rim of the front lid | 1.0 mm normal to the lid | 1.0 mm radius | Initial 45° bevel; top-face inset about 0.586 mm |
| Lid's front corners in plan view | Matches the wall profile at the underside | Compensated ellipse in the lid plane | The 10° lid angle is accounted for |

Treatment depth and blend radius are separate dimensions. The result is a subtle softened edge, with flat joining regions and the original mounting axes retained.

The front/top cut crosses the panel-to-wall seams in one common assembly profile. The side-wall/front-panel butt joints remain flush; hidden seam edges are not rounded independently. Both front corners are mirrored.

The lid is still a **4 mm screw-fastened cover**. Its underside has the existing **1 mm vertical clearance** above the sloping wall and panel tops, with the original top blocks providing support. The monitor stop, screw bores and their bearing regions remain. The lid's side-rim treatment tapers from the full amount at **Y = 48 mm** to zero at **Y = 60 mm**, measured in the lid's underside reference coordinates, preserving the rear region that joins the bezels.

## Small front-corner test kit

Print these three new exact crop pieces:

| Sample | Source enclosure part | Role |
|---|---|---|
| `front_corner_wall_fit.stl` | `left_front_wall` | Left front corner and side fastener holes |
| `front_corner_panel_fit.stl` | `front_button_panel` | Front panel, matching upper edge and corner screw |
| `front_corner_lid_fit.stl` | `front_cable_lid` | Rounded lid corner and original top screw |

These are assembly-coordinate crops at **X = 0…40, Y = −1…40, Z = 40…100 mm**, independently rotated onto their real print faces. The samples are roughly 40 mm across, with 4 mm shell thickness. Their artificial crop edges remain square.

The assembled test uses **two existing mounting pieces**:

- `corner_left_front_56.stl`
- `top_block_left_25.stl`

Reuse these mounts if already printed, or print the originals included in the corner-test download. The complete test kit therefore contains **five STLs: three new panel samples plus two unchanged mounts**. It uses the same M3 hardware as those mounts. It does not add any enclosure parts.

### Assemble the corner test

1. Stand the side-wall and front-panel crops with their **Z = 40 crop bottoms on the same flat surface**. The panel goes inside the side wall at X = 4 mm, with both front surfaces flush.
2. Install the upper corner bracket using the two original holes at **Y = 14 / Z = 56** in the wall and **X = 14 / Z = 56** in the panel. Fit the existing captive nuts and M3 fasteners.
3. Attach the original top block to the side-wall hole at **Y = 31 / Z ≈ 71.408 mm**. Its sloping top locates the lid at the original height.
4. Place the lid sample on the top block and fasten it through the **X = 10 / Y = 25** hole. Hold the outside outline aligned while tightening gently. The lid should retain its **1 mm vertical gap** above the wall and panel.
5. Check the feel of the real front corner, the joined profile, and the printed curved/beveled edge. The square crop boundaries are not finished cabinet edges.

All three sample panels print **outside/show face down**, as exported. The same orientation applies to their full enclosure parts. The new bevel starts at 45° and blends into the adjacent surface, avoiding the steep start of an ordinary bottom fillet. Actual printer settings, material, fit, and surface feel still require this small physical test. This is not a blanket support-free claim for every other feature on the existing panels.

`front_corner_kit.json` records the crop, source parts, dimensions, and assembly instructions. `front_corner_preview_meshes.json` and `front_corner_before_meshes.json` retain assembled positions for exact before/after renders.

## Retained controls and mechanical interfaces

The following features are carried forward from V1.10 and V1.9.

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
4. If the printed aperture needs adjustment, the same recessed sample is available as `nudge_mx_14p0.stl` and `nudge_mx_14p2.stl`. The default `nudge_switch_fit` filename was introduced in V1.10 in place of `nudge_mx_14p1` and is retained unchanged.

These dimensions retain the existing **MX-style switch assumption**. They are not a guarantee for an unmeasured switch variant. A successful test of the actual hardware is the fit criterion.

The samples and full walls are exported **outer face down**, so the wide recess mouth faces the bed and the internal reinforcement faces upward. Keep the same orientation and relevant slicer settings for the sample and wall. The tapered well is 45°, but the mounting face includes a **1.95 mm ledge on each side** of the aperture. That ledge may need tuned bridging or local support; support-free printing has not been physically verified. Inspect the sliced layers and printed clip edges before committing to the full walls.

## Flipper reinforcement and matching floor retained from V1.9

Each inside flipper reinforcement remains a broad D-shaped pedestal: **46 mm nominal root width**, **44 mm flat inside-face width**, and **8 mm total thickness**, continuing down to **Z = 0**. The upper circular collar, flat nut bearing area, original **Ø28** bore at **Y = 103 / Z = 30**, and wall screw axes are retained.

Use the existing **V1.9 notched front floor**, which is unchanged in V1.11. Its two edge notches run through the 4 mm floor at:

| Side | X bounds | Y bounds |
|---|---|---|
| Left | 4.3…8.3 | 79.7…126.3 |
| Right | 251.7…255.7 | 79.7…126.3 |

The full-height pedestal has **0.3 mm modeled clearance** from the floor. The unnotched V1.8 floor still overlaps the pedestal and is not a direct substitute. No additional fasteners, brackets, or enclosure pieces are required.

The combined `flipper_nudge_wall_sample.stl` includes the retained pedestal and the V1.10 recessed switch opening. Its adjoining `flipper_floor_notch_sample.stl` is unchanged from V1.9. Those larger samples remain available when checking the whole control assembly and floor joint.

There are **20 separate fit samples**, including the three new corner crops, in addition to the **45 enclosure STLs**. All enclosure parts retain an 8 mm brim allowance on a 325 × 325 × 315 mm printer.

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
python render_v1_11_details.py
```

The builder exports the STEP assembly, **45 print-oriented enclosure STLs**, **20 fit samples** (the 17 retained samples and three new corner samples), inventory, manifest, and assembly-position meshes. It checks valid single solids, printer bounds, printed-part overlap, reserved hardware spaces, and cross-control clearance.

Reports are `geometry_checks.json`, `v1_11_feature_checks.json`, and `stl_mesh_checks.json`. The new checks compare the real side-wall/panel profiles across each butt seam, verify preserved mounting and bearing regions, check the lid's rear bezel interface and matched plan-view corner, and confirm that each corner sample is an exact crop of its full part. Prior control, pedestal, floor, fan, and hardware-reserve checks are retained. Failed features or unintended interference stop the build.

The mesh validation checks actual exported vertices, closed manifold edges, consistent winding, a single connected shell, positive signed volume, and print-bed placement. Exact CAD and mesh checks do not establish the feel, strength, tolerances, or finish of a physical print.

The preview mesh file contains only the 45 printable enclosure parts. STEP adds clearly named nonprinted hardware/reference envelopes. All earlier version source and outputs remain separate.

## Printing references

- [Prusa: Modeling with 3D printing in mind](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135), including the bottom-fillet versus chamfer guidance.
- [3DVerkstan: Getting better prints](https://support.3dverkstan.se/article/30-getting-better-prints), including a chamfer with a rounded upper transition.
