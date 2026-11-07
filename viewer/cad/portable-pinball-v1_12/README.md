# Portable Pinball V1.12 — Modular adjustable feet

**Design prototype; do not install on a populated cabinet without a small fit test and load testing.** The original V1.11 model, monitor geometry, controls and front-corner treatment are retained. This is an independently selectable Studio version.

## Layout (millimetres)

- Four stations at X=48 and 212, front Y=80 and rear Y=438. Station center separation is 164 mm laterally, 358 mm front to rear.
- Existing 4 mm removable bottom panels receive sixteen new 4.5 mm M4 clearance holes (four per station). No changes to the original floor mounting screw bores, notches or PC slots.
- Each 50 mm diameter bottom receiver has an 8 mm flange and a 30 mm diameter by 10 mm boss. Four M4 through-bolts at ±13 mm X/Y squeeze the floor between the receiver and its 50 mm × 5 mm upper backing plate.
- Four upper backing plates contain four nominal M4 hex-nut pockets each. Verify with actual nuts and washers; no printed fastener threads are used.
- Each underfloor receiver and each extension have hex pockets sized for nominal M8 hardware (pocket 15.5 mm across polygon vertices, approx. 13.42 mm across flats; 7.2 mm nominal end pockets), with 8.7 mm central passages. Use real steel M8 nuts and short steel threaded studs, properly locked. Do not treat the printed hex cavities as threads.
- All four mounting receivers are interchangeable; round spacers are 30 mm diameter, modular lengths 20 and 40 mm. Four terminal adapters are 36 mm diameter × 20 mm tall.
- The V1.12 preview uses one 20 mm extension at each front corner and a 20 + 40 mm pair at each rear corner. This creates **40 mm additional nominal rear lift** relative to the front, over a 358 mm center distance, equivalent to about **6.4 degrees of added body tilt** if all four feet make flat contact. The cabinet's screen already has its own 10-degree built-in slope; combined viewing and ball-physics angles must be checked in the actual location.
- The four **rubber swivel feet are visual references only** in the 3D viewer, not printable. Each is modeled as a nominal 40 mm pad with M8 stem; buy suitable swivel leveling feet and verify actual stem length, thread form, load rating, and available joint travel. The swivel lets each pad contact the tabletop when the cabinet pitches. The CAD display keeps all assembly axes vertical for inspection, so rear feet appear lower than front until the cabinet is physically tilted.

## Hardware and safety checks

1. Print one receiver, one backing plate, one 20 mm extension, and one terminal adapter. Verify M4 and M8 nut/stud fit. Inspect the receiver-to-extension shoulder; fully tighten hardware without splitting plastic. Never rely on friction-only installed nuts; use a suitable secure-retention approach compatible with the chosen material and metal hardware.
2. Mount the first station to a scrap 4 mm printed floor coupon using four M4 bolts and broad washers. Check that neither plate warps or cracks. Recheck load and rocking under simulated side-button and nudge forces.
3. The cabinet floor is removable and previously supported by small wall blocks; **this prototype does not prove that the floor-to-wall joints carry the cabinet's entire weight safely**. For permanent legs, test/reinforce floor supports or attach load paths directly to the side walls, and check screw engagement before installation.
4. Use matching spacer combinations left/right at each end. Never raise one side alone. Rear 40 mm difference is an illustration, not a recommended maximum or a guaranteed comfortable viewing angle.
5. Commercial swivel pads and rubber are deliberately excluded from STLs and print inventory. Confirm rubber pads and ball joints cannot bottom out over the intended adjustment range. Keep feet within the tabletop footprint and avoid tip hazards.
6. No printed part should be used as a structural support before physical print, fastening, and static/dynamic load testing. Suggested starting point: PETG, 5+ walls, high infill, with a dedicated load coupon; adapt to your material and printer.

## Studio & download contents

- 63 independently selectable printable CAD parts (the original 45 with 18 new mounting/leg components), plus three original envelopes and four visible reference rubber feet.
- `stl-v1_12/`: 63 print-oriented STLs. Receivers are flipped flange-down for better printability. The four feet-reference meshes are not printable and have no STL.
- `fit-tests-v1_12/`: all 20 original small fit tests retained; check the original corner and switch issues before printing whole enclosure.
- `cad-print-pack-v1_12.zip`: full STEP, STLs, all small fit tests, source CAD, manifest and CAD validation checks.
- Select any receiver, spacer, cap, or backing plate in Studio's Parts dropdown to inspect it and export its individual STL.

**Verification:** CAD solids, nominal geometric clearances, print-bed envelopes, control and PC keepouts passed automated geometry checks. Real-world threaded hardware sizing, pad articulation, strength, load sharing, print quality and tabletop stability have not been tested.
