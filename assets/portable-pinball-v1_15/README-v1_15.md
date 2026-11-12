# Portable Pinball V1.15 — Adjustable feet converted to M6

V1.14 and all earlier versions are preserved. **Only the modular feet, their M6 pad references and local mounting geometry change.** The cabinet body, monitor supports, floor locations, controls, flipper/nudge mounts and other parts remain unchanged. All measurements are in millimetres.

## Hardware to assemble the modeled four feet

- **Eight M6 × 30 mm bolts**: each 20 mm section (two per front foot, two per rear foot).
- **Two M6 × 50 mm bolts**: each 40 mm rear section (one per rear foot).
- **Fourteen standard M6 hex nuts**: 4 receivers, 4 first extensions, 2 second rear extensions and 4 terminal swivel-pad adapters.
- **Four commercially purchased M6 threaded swivel rubber feet** (illustrative geometry only): nominal 40 mm contact pads; choose stems that reach the center nut (about 11–17 mm into the terminal, typically 20 mm), and check physical swivel range.
- The original **16 M4 floor mounting bolts and nuts**, plus appropriate washers, are still required. The mounting plate and floor hole locations are unchanged.

Standard M6 nuts are nominally 10 mm across flats and about 5 mm thick; pocket target is approximately 10.5 mm across flats (12.1 mm across vertices) and 6 mm high, with a 10.95 mm slide-in throat. These are **printer-dependent nominal dimensions**, not proof of actual nut fit. Bolt lengths refer to standard under-head shank lengths. Head access countersinks are nominal Ø16 mm × 6.5 mm deep, accommodating many M6 hex/socket bolt heads but NOT every tool/socket; verify your exact hardware and tightening tool before printing a full set. No M8 hardware is needed in V1.15 feet.

## How the stacked pieces connect

Each bolt is inserted **upward from the underside of the piece it secures** into a sideways-loaded M6 nut in the part immediately above. The connections alternate between two off-center X positions (A/B), so a bolt head and the next nut pocket do not collide. The nut cannot escape laterally once the bolt is installed through the constrained axial bore. A small printed entry nib supplies *light* friction retention before installation; file/trim it if a test-fit nut binds rather than forcing it.

For each **front** foot: slide nut A into the underside receiver; install the 20 mm extension with M6×30 bolt A; slide nut B into the extension; fasten the 20 mm terminal with M6×30 bolt B; slide a CENTER M6 nut into the terminal to receive the purchased swivel foot. For each **rear** foot: receiver nut A -> 20 mm extension with M6×30 bolt A -> nut B -> 40 mm extension with M6×50 bolt B -> nut A -> 20 mm terminal with M6×30 bolt A -> center M6 nut and M6 swivel pad.

The enlarged receiver boss would otherwise block access to the four original M4 flange screws. V1.15 therefore includes **four 10 mm diameter access tunnels through each boss** to the original recessed M4 bolt heads. Use a screw head and driver that fit the tunnels; inspect the thinner surrounding printed material carefully.

## Print-first verification (required)

1. First print ONE `foot_receiver_left_rear.stl`, ONE `foot_extension_left_rear_1_20mm.stl`, ONE `foot_extension_left_rear_2_40mm.stl`, and ONE `foot_terminal_left_rear.stl`. The exact full pieces are compact fit samples; a complete cabinet print is unnecessary.
2. Slide in your actual M6 nuts and verify that the nut traps accept each bolt without spin or cracking, and that M6×30/50 shanks reach the intended upper nut while stopping before contacting the cabinet floor.
3. Confirm the **M4 bolts can actually be installed and tightened through the receiver's access tunnels**, and the loaded flange/4 mm floor/backing plate are rigid.
4. Confirm the M6 commercial swivel-pad stem length, nut engagement, pad pivot range, and rubber grip on the intended tabletop.
5. Print in PETG with generous walls and strong layer adhesion, then test static load, lateral button/nudge force and rocking on a bench. The original floor-to-wall load path has **not** been proven to support elevated feet. Do not use the raised feet on a finished monitor cabinet until a physical load test passes.

The CAD builder checks each of the 63 printable solids and 20 fit STLs for print envelopes, valid volumes and component clearances. Separate mesh validation confirmed 83 closed, manifold STLs. All are design-only checks. **No nut fit, screw fit, grip strength, printing or full-cabinet load test has been performed.**
