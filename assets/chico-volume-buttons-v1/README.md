# Chico volume buttons V1 — standalone 3D printable model

Two independent momentary volume controls using the user's BLACK, nominal 12x12mm tactile switches.
Not part of the large pinball cabinet model.

## Construction and retention
- Rounded case 78 x 32 x 17.8mm total (back 15mm, front 2.8mm).
- Two 15.3mm printed button heads slide in Ø16.1mm faceplate bores.
- The 20.3mm diameter x 1.5mm rear flange on EACH cap is **larger than the hole**:
  insert caps from the inside before closing. They physically cannot fall out the front.
- The tactile spring returns each cap, and the flange stops against the underside of cover.
- Two front M3 screws secure into heat-set inserts in rear pillars x +/- 33.1mm.
- User's nominal M3 5mm OD x 6mm inserts: 4.5mm pilot pocket, 6.9mm usable depth,
  insert from open front of rear shell, not through its back. Check real insert size.
- 9 x 6.8mm cable notch in rear shell's side (+Y), with a covered rear floor.
- Two optional rear mounting holes accept 3mm screws through the tray floor before assembly.
- Switch pockets assume **12 x 12mm body**. Both sides remain accessible for wiring.
  Secure each switch to its support with a small removable glue bead or suitable thin PCB,
  not on metal/switch actuator. Never pull on bare solder legs.
- Faceplate prevents button escape; faceplate is removable to replace a switch or cap.
- 3 standard cap stems plus shorter and longer versions (same diameter, 1.9 / 3.4 /
  4.9mm length measured beyond rear flange). Use ONE minus and ONE plus cap, same length.
  Switch actuation heights not measured: verify that each cap clicks and returns freely,
  without constantly actuating. Stop and adjust if not; physical switch fit is pending.
- PETG suggested, 0.2mm layers, 4 walls, 25-35% infill. Print cap faces DOWN,
  body base DOWN, faceplate outer face DOWN. Letter marks recessed .7mm.
- Print switch_12mm_fit_gauge and m3_insert_fit_coupon **first**. Coupon bores:
  4.3 / 4.5 / 4.7mm nominal; 5mm inserts must be tested with your actual printer.

## Wiring
- Black 4-leg switch normally has 2 legs on each electrically common side. Verify with
  a multimeter: use one pin from each opposite side for a normally-open button.
- Route both switch wires through side notch; strain relieve them to the cabinet.
- Connect to TWO spare, separate USB encoder inputs and GND if available.
  Map encoder key outputs to Windows system Volume Up / Volume Down (software mapping may
  be necessary; keyboard HID codes depend on the encoder). Do not apply amp power to switch.

## CAD and status
- Exact CAD generated in CadQuery; STL / STEP for each part in ZIP.
- GLB preview has illustrated switch bodies and the cover **exploded upward** so rear
  flanges and heat-set bosses are visible. Printed STL files are NOT exploded.
- Computer-validated manifold meshes only. Actual switches, screw clearance,
  insert heating and mounted actuation remain to be tested.
