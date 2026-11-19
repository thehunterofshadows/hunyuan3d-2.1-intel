# Chico volume buttons V4 — standalone 3D printable model

Two independent momentary volume controls using the user's BLACK, nominal 12x12mm tactile switches.
Not part of the large pinball cabinet model.

## Construction and retention
- Rounded case 78 x 32 x 18.4mm to top of raised cover trim (back 15mm, faceplate base 2.8mm, accents 0.6mm). The caps protrude beyond this.
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
- Three full-width back lengths: 3.5 / 4.9 / 6.5mm total below head (short,
  standard, long). Use ONE minus and ONE plus cap of the same selected length.
  The standard cap is engineered to touch the illustrated switch at rest:
  nominal 0.5-1mm compression travel available before adjacent pocket ribs,
  but **actual switch height/throw are unmeasured**. Try before mounting.
- V3 preserved: The + and - on the cap faces are PHYSICALLY RAISED 0.60mm, not cut
  into the faces. The faceplate has a raised 0.60mm 'VOLUME' title, horizontal
  lines on both sides, and a 1.0mm-wide raised rounded-rectangle border.
  All accent features begin together at the same height for a clean color swap.
- NEW V4: Both + and - cap heads are 7.0 mm tall (previously 4.5 mm),
  plus 0.60 mm of raised sign above the head. Rear flange lengths, switch travel,
  faceplate and screw geometry are unchanged.
- Printing: PETG, 0.20mm layers, 4 walls, 25-35% infill. Print cap wide
  backs **DOWN** (lettered face UP), and faceplate back (z=0) **DOWN**,
  raised-lettered front UP. Print without ironing the raised accent.
  Print cover and caps as SEPARATE PLATES because their swaps occur at
  different Z heights:
    * Faceplate: base surface Z=2.8mm, swap just BEFORE the first layer ABOVE it (usually print Z=3.0mm for 0.20mm layers).
    * Standard caps: base face Z=11.9mm, swap just BEFORE first layer above it (usually print Z=12.0mm).
    * Short caps: base face Z=10.5mm, swap just BEFORE first layer above it (usually print Z=10.6mm).
    * Long caps: base face Z=13.5mm, swap just BEFORE first layer above it (usually print Z=13.6mm).
  Each accent is 0.60mm tall: 3 full layers at 0.20mm layer height.
  Slicer-specific pause behavior varies: inspect the layer preview to verify
  the raised details are the first geometry printed in the second color.
  Top-face two-color trim is achieved by ONE filament change PER PRINT JOB,
  with the body printed in one color and the relief details in another.
  No AMS/MMU is required. Do not print faceplate face down or accents will
  touch the build plate and cannot be color-swapped at the end.
  0.20mm layer height is necessary for these listed Z-levels.
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
- V1–V3 are preserved and remain available through a single model's version selector. V4 lengthens BOTH cap heads.
