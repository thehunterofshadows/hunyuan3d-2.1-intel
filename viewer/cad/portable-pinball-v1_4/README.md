# V1.4 fit correction — right monitor saddles

Both right bearing shelves are raised 5 mm for the measured 7 mm right housing versus 12 mm left housing. Use the same 2 mm padding; do not add another 5 mm shim on these revised shelves. Mounting bores, locator faces, left saddles and all other printable parts retain V1.3 geometry. Reference monitor remains a conservative uniform 12 mm envelope, not an exact stepped housing model. Physical fit remains pending.

# Portable Mini Virtual Pinball Cabinet — CAD Prototype V1.4

**Print the small fit tests first. Full enclosure files are provisional, not a verified production design.**

This package contains real parametric CAD, an assembled STEP model, 45 individually oriented enclosure/fitting STLs, 10 test/optional-shim STLs, and previews generated directly from those solids. Hardware, foam, wiring and speakers are not included as printable parts. Reference objects in STEP are colored clearance envelopes, not exact monitor or PC models.

## Current layout

- Body: 260 mm wide × 470 mm long. Front height 75 mm; rear 157.87 mm. Sloped top at 10°. Covers add approximately 5 mm above the body; the hatch sits above its deck.
- Coordinates: X left-to-right, Y player/front-to-rear, Z upward from the body bottom. This package uses millimeters throughout.
- Monitor: measured 358.8 × 223.8 mm; housing 7–12 mm. Front edge Y=64, rear edge Y≈417.35. HDMI/USB-C front-left; monitor controls and headphone jack rear-left.
- Folded cover: reserve 35 mm total depth below the screen plane in the central area. The outer 5 mm strips are provisionally reserved for padded rigid-housing support. This is an assumption requiring a physical fit test.
- Four edge saddles with side locator stops. Add 2 mm padding. A 5 mm shim is available where a saddle meets the 7 mm thin housing. Do not compress the cover or use it to support the monitor.
- Side bezel rails and the front/rear deck have approximately 1 mm projected overlap over the outside housing. They are retainers with approximately 1 mm clearance above the screen-plane reference, not clamps on the glass. Confirm overlap does not encroach on active pixels.
- Two housing end stops are built into the undersides of the front and rear lids at the **right-hand** corners, clear of the left-hand ports and controls. Stops nominally leave 0.5 mm longitudinal clearance at each end. Side locator stops leave about 0.5 mm per side locally; this refines the earlier schematic's 1 mm-per-side pocket assumption. Fit-test before committing to this tighter location system.
- All five game-button mounting holes: 28 mm. Body/wiring allowance: 45 mm inward from each mounting panel, with a provisional 40 × 40 mm cross-section.
- Front buttons: centers X=110 / 160 / 210 mm; Z=26 mm (Start / Exit / Launch). They have been shifted right from the schematic to keep the front-left cable drop clear and avoid the right corner bracket.
- Side flippers: Y=103 mm, Z=30 mm. Position is provisional; check comfort before printing wall panels.
- PC allowance: 190 × 190 × 45 mm, X=35–225, Y=240–430, Z=13–58. Install Dell ports toward the player, giving connector space ahead of the PC. Secure with straps through rear-floor slots, with 9 mm spacing/padding above the 4 mm floor. Use stick-on rubber feet at least 5 mm tall under the cabinet to clear screw heads and straps. The rear removable floor serves as the PC tray.
- USB encoder reference: 70 × 50 × 12 mm at X=100–170, Y=140–190, Z=13–25. It is a reserved volume, not a printed mount.
- Audio from the Dell to powered speakers; speaker housings/mounts have not been designed. Monitor headphone access is retained. PC and monitor power bricks remain outside.
- Front cable-lid region: about 60 mm outward from the monitor. Keep the front-left drop clear. Rear hatch: approximately 80 × 35 mm clear opening with a larger screw-retained lid. Connector, finger and cable-bend fit must be checked physically.

## Open these files

- `exports/mini_vpin_assembly.step`: CAD assembly with all parts in assembled positions, plus clearly named REFERENCE objects.
- `exports/enclosure_stl/`: full prototype parts, each already rotated onto its intended print face and placed on Z=0. Import at 100% scale; do not auto-scale.
- `exports/print_first_tests/`: small fit-test and optional shim files.
- `exports/cad_preview.png`: assembled/exploded actual CAD preview.
- `exports/fit_test_preview.png`: actual STL test-piece preview.
- `exports/print_inventory.csv`: all enclosure parts, print bounding boxes and orientation labels. One of each file produces the 45-piece assembly; many small brackets/blocks are repeated geometries at different assembly locations.
- `exports/geometry_checks.json`: solid and clearance checks.
- `exports/stl_mesh_checks.json`: mesh checks for all 55 STL exports.
- `parameters.json` + `build_cabinet.py`: editable parametric source. Requires Python 3 and CadQuery 2.7.0. Run from any directory with `python build_cabinet.py`.

Do not print the STEP reference envelopes. Only print the provided STLs. The test files are already normalized to the bed individually and are not intended to assemble at their STL origin coordinates.

## First print — wall joint (3 parts)

Print `joint_front_wall.stl`, `joint_rear_wall.stl`, and `joint_splice_plate.stl` in their supplied orientation. The two wall samples meet at the original center seam; their bottom edges share the same datum. Slide the 8 mm tall tongue into the matching notch, leaving the 0.3 mm butt gap, then install the splice inside the cabinet wall using four M3 ×12 screws and nuts. Do not glue.

Pass criteria:
1. Tongue enters with finger pressure, without hammering, splitting or excessive rocking.
2. Four splice holes align without forcing either wall sample.
3. Tightening with light hand pressure makes the joint rigid, without cracking the print.
4. If the tongue binds, report how much additional clearance is needed; avoid filing away the only dimensional evidence before measuring.

## Second print — monitor edge (3 parts)

Print `monitor_edge_cradle_12mm.stl`, `monitor_retaining_bar.stl`, and `monitor_5mm_shim_for_7mm_housing.stl`. Their supplied orientations minimize overhangs. The cradle has a narrow padded ledge and open space underneath for the attached cover.

1. Put a **2 mm thick, approximately 5 mm wide** foam strip on the narrow shelf. Keep it on rigid housing, clear of the folded cover.
2. Set an exposed housing edge about 0.5 mm clear of the upright locator. Keep the rest of the monitor supported on a soft surface at the same height; one coupon must never carry the whole monitor.
3. For a 12 mm housing section, use the padding alone. For 7 mm housing, put the 5 mm shim on the shelf first, then padding.
4. Fit the retaining cap over the outside of the upright. The screw holes match at Z=46 mm. Use two M3 ×10 screws gently into the 2.8 mm pilot holes **for this test only**. Do not torque them hard; the full cabinet uses through bolts and nuts. The cap underside is at Z=52 mm; padded housing top targets Z=51 mm, leaving about 1 mm gap.
5. Check that the cap only overlaps the housing edge by about 1–1.5 mm, does not touch the active screen, and can be removed without forcing or flexing the monitor.
6. Test a thin and thick section. Check the cover has free space below and does not prevent housing support. Send a close-up of the fit with the padding and cap installed.

Do not force a fit, clamp the glass or attach adhesive to the monitor. Tape/adhesive for padding or shims goes on the printed cradle only.

`optional_saddle_shim_5mm.stl` is a shorter 5 ×20 ×5 mm shim for the four full-cabinet saddles. It is not required for the long monitor test coupon. Print as needed after confirming the actual support locations.

## Third print — button hole

Start with `button_hole_28.stl`. If an actual button barrel will not pass comfortably, try `button_hole_28p2.stl` and then `button_hole_28p4.stl`. These are 4 mm thick panels with modeled holes of 28.0, 28.2 and 28.4 mm, respectively. The CAD full-panel hole remains 28.0 until the test determines otherwise.

Verify barrel, retaining nut, thread engagement, switch assembly and connected-wire depth. A correct hole alone does not establish that the complete button fits. Actual buttons have not been selected; internal depth and body cross-section are provisional.

## Print strategy

QIDI lists the X-Max 3 build volume as **325 ×325 ×315 mm**: https://qidi3d.com/products/qidi-x-max-3 . Exports are checked against that envelope with an extra **8 mm brim allowance on each XY side**. The largest modeled XY extent is 260 mm. Heights and bed orientation are listed individually in `print_inventory.csv`.

- Walls/end plates: broad outside face on bed. Side wedge panels are split at Y=235 mm; all holes and vents print vertically through their flat print orientation.
- Bottom panels: broad flat underside on bed.
- Bezel rails: outside/top face on bed.
- Front cable lid/rear deck: outside/top face on bed, with the housing stops growing upward. The rear deck's underside hatch-nut pockets open upward in this orientation.
- Control hatch: top face on bed; lift-out after removing its two screws. A small notch provides clearance above the left main-deck fastener.
- Corner brackets, floor blocks, top blocks and saddles: supplied flat foot on bed. Small horizontal 3.4 mm screw bores are short bridges; inspect their first samples. Supports are intended to be off, not trapped inside the bores or nut pockets. If a hole prints tight, hand-clear it with the appropriate drill while the part is off the monitor.
- Test cradle: base on bed, 45° gusset beneath its narrow ledge. Retaining cap is exported top-face-down.

Provisional slicing starting point: your normal calibrated filament profile, 0.4 mm nozzle, 0.20 mm layers, 4 perimeters, 6 top/bottom layers, about 25% infill for blocks. Flat 4 mm panels may be mostly solid under these settings. Use a brim where needed; leave auto supports off initially for the small tests and inspect slicer layer previews. No print times or filament consumption are claimed; obtain those from your slicer. No G-code is included.

PLA is suitable for checking the small test shapes. Choose the full-cabinet material after confirming operating temperatures around the enclosed PC; the CAD package does not establish thermal performance. Use the filament's own temperature/profile settings.

## Provisional hardware list

Use standard M3 nuts; hex pockets are modeled 6.6 mm across corners. Test fit with your nuts before large prints. Light press fit or removable tape on the *printed part* can retain the hatch nuts during assembly; do not put adhesive on the monitor. Socket-head screws are not countersunk: use external feet so floor screw heads do not contact the tabletop.

| Connection | Screws | Nuts |
|---|---:|---:|
| 8 corner brackets, 2 screws each | 16 × M3 ×12 | 16 |
| 2 side splice plates | 8 × M3 ×12 | 8 |
| Floor shelf blocks to walls | 8 × M3 ×25 | 8 |
| Removable floor panels to shelf blocks | 8 × M3 ×12 | 8 |
| Top fastening blocks to walls | 10 × M3 ×20 | 10 |
| Bezel rails, cable lid, rear deck to top blocks | 10 × M3 ×10 | 10 |
| 4 monitor saddles to side walls | 4 × M3 ×30 | 4 |
| Control-access hatch | 2 × M3 ×10 | 2 |
| Small monitor coupon only | 2 × M3 ×10, lightly into plastic | none |

Full assembly nominal total: 66 M3 screws and 66 nuts, plus the two temporary coupon screws. Confirm lengths with actual heads/washers and nut thickness; neither hardware interference nor fastener torque has been simulated. Use flat washers where needed and allow a little extra screw length if washers are added. Foam, straps, feet, encoder, buttons, cables, speakers and PC remain user-supplied.

## Assembly order (after fit approval)

1. Bolt each side's front/rear walls together with the splice plates; check tongue clearance.
2. Attach the front and rear end plates using the corner brackets. Tighten square on a flat surface.
3. Fit floor shelf blocks, top fastening blocks and padded monitor saddles with their accessible through nuts. Load the floor/top block hex nuts before closing them with panels.
4. Fit both removable floor panels. Strap the PC to the rear tray and mount the encoder using a removable method appropriate to the actual board. Keep PC intake/exhaust open and PC ports facing the player.
5. Install game buttons and wire them. Leave the left front cable channel clear. Check wired button depth before installing the monitor.
6. Dry-fit monitor and attached cover on the padded rigid-housing saddles. Add the 5 mm shims only where the thin housing needs them; verify all contacts and the actual housing step. Do not rely on a shim location inferred solely from this prototype.
7. Connect the actual monitor cables, route them down the left-front channel and secure the cable jackets to the enclosure with slack at connectors. Verify the cable lid and button hardware can coexist.
8. Install the front cable lid with its housing stop, rear deck with its housing stop, and side bezel rails. Retainers must have clearance and never load the glass.
9. Install the rear control hatch and verify Power/Menu, +/− and headphone access after removal. Main rear-deck left screw is accessed beneath the hatch notch.
10. Check stability, handling, access and cable strain. Run the PC/display and check heat and ventilation before calling the design finished. Generic vents have been provided; fan placement/ducting and speaker mounting remain unresolved.

## Verification performed

- Every printable enclosure part passes OpenCascade validity and is one solid.
- All enclosure parts fit the printer build volume including the stated 8 mm XY brim allowance.
- All 55 STL meshes have closed edge incidence and no degenerate triangles at the export-check tolerance.
- Pairwise intersection checks found no modeled solid overlap among printable enclosure parts.
- Reserved PC, button bodies, central folded-cover volume and encoder allowance do not intersect the modeled printed parts.

These checks do **not** prove real-world fit, heat performance, print strength, ergonomics, cable bend radii or safe bezel contact. The monitor's active-area boundary, folded-cover shape, housing-step direction, actual PC connectors and exact buttons still require checking. This package deliberately keeps the full-cabinet parts provisional until those fit tests pass.

## V1.1 reinforced monitor supports
All four locator lips increased from 3 to 6 mm outward toward the cabinet wall. Monitor-facing locator faces and padded shelf heights are unchanged. An external 4 mm wide × 8 mm high triangular root brace strengthens each lip. The projecting bearing shelves also gain 4 mm underneath, from 14 to 18 mm at their centers; padded top elevations and mounting holes stay unchanged. Support STLs now lie on an end face, making each layer include the lip/base profile. Print one support and check the actual monitor/cover fit before the full set; strength has not been physically tested. All other part geometry is unchanged.

## V1.2 A1/A2 right bezel consolidation
The parts named `bezel_right_front` (A1) and `bezel_right_rear` (A2) have been replaced by **one printed part** named `bezel_right_a1_a2`. The rail spans approximately 351.35 mm in the assembled cabinet. Its outside geometry, 1 mm housing overlap, slope, and two M3 mounting holes at Y=140 and Y=330 mm are preserved. The only new area fills the former 0.3 mm joint at the sidewall seam. The left-side bezel remains two pieces. The right-side rail STL is oriented 45 degrees across the QIDI X-Max 3 bed; do not straighten it in the slicer. Inspect first-layer/brim fit and use your calibrated PETG settings. The former V1.1 package is preserved for comparison. Physical monitor and screw fit remain unverified.

## V1.3 one-piece bezels on both sides
Merged `bezel_left_front` and `bezel_left_rear` into **`bezel_left_one_piece`**, matching the already merged V1.2 right-side `bezel_right_a1_a2`. The assembled length of each bezel is about 351.35 mm. Both are rotated 45° for 325×325 mm QIDI X-Max 3 printing. No housing overlap, upper clearance, two M3 screw locations per side, or any of the other 44 CAD solids are modified. The cabinet now has **45 printed solids** + 3 reference envelopes. Individual left/right STLs, full CAD pack, STEP and GLB exported as V1.3; previous revisions archived. Prints and monitor clearance remain to be physically verified.
