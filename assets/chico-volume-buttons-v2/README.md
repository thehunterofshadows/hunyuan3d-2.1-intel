# Chico volume buttons V2 — standalone 3D printable model

Two independent momentary volume controls using the user's BLACK, nominal 12x12mm tactile switches.
Not part of the large pinball cabinet model.

## Construction and retention
- Rounded case 78 x 32 x 17.8mm total (back 15mm, front 2.8mm).
- Two 15.3mm printed button heads slide in Ø16.1mm faceplate bores.
- The rear of EACH cap is a solid **Ø20.3mm-wide cylindrical pad** extending to
  the tactile switch contact (no skinny plunger). Its diameter is larger than the
  Ø16.1mm faceplate opening: insert from the inside before closing. It cannot fall out.
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
- The prior Ø4.8mm narrow plunger has been removed on both + and - buttons.
  The **Ø20.3mm retaining lip now continues all the way to the flat switch-contact face**.
  This makes each cap printable with its full-width 20.3mm back on the build plate.
  Cap head remains Ø15.3mm, moves freely inside the Ø16.1mm faceplate opening.
- Three full-width back lengths: 3.4 / 4.9 / 6.4mm total below head (short,
  standard, long). Use ONE minus and ONE plus cap of the same selected length.
  The standard cap is engineered to touch the illustrated switch at rest:
  nominal 0.5-1mm compression travel available before adjacent pocket ribs,
  but **actual switch height/throw are unmeasured**. Try before mounting.
- PETG suggested, 0.2mm layers, 4 walls, 25-35% infill.
  Print caps **large flat underside DOWN**, symbols UP; body base DOWN,
  faceplate outer face DOWN. Letter marks recessed 0.7mm.
  The large button base removes the fragile small-foot print orientation.
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
- Computer-validated manifold meshes and nominal assembled-fit check only.
  Actual switch geometry, actuation, insert heating and fit remain to be tested.
- V1 is preserved unchanged. V2 is a separate selectable studio model.
