# Portable Pinball V1.20 — direct M8 front rubber feet

## What to print
Only TWO replacement parts are required for an existing V1.19 cabinet:
- `stl-v1_20/foot_receiver_left_front.stl`
- `stl-v1_20/foot_receiver_right_front.stl`

Optional fit tests: print `m8_nut_fit_coupon.stl` before a receiver, and `front_m8_center_pilot_jig.stl` to locate the exact center of the front mounting holes.

**Do not reprint** either floor panel, either upper front backing plate, or any rear parts. They are unchanged.

## Hardware and installation
- Reuse all four existing **M5 mounting bolts and captive M5 nuts per receiver** (8 front mounting bolts/nuts total). Check that the socket fits the existing 17 mm tunnels. Use verified short bolts, not M5×30.
- Install a **standard metal M8 hex nut in the TOP opening** of each new front receiver *before* sandwiching the cabinet floor; the cabinet floor retains the nut. No M6 nut clip or 55 mm M6-to-M8 front extension is needed.
- The receiver's hex pocket is **15.5 mm across corners**, about 13.42 mm across flats, nominally 8 mm deep. The centered **Ø9.0 mm through-bore** extends through the entire **20 mm** receiver. Test with your actual M8 metal nuts and M8 foot stems, not only against a nominal specification.
- **Existing original front cabinet floor and front backing plates DO NOT have an M8 hole yet.** Drill a centered **Ø9.0 mm** hole through BOTH the 4 mm front floor panel and the 6 mm inner backing plate at EACH front foot station. Center locations in original cabinet coordinates: **(X=48,Y=80) and (X=212,Y=80) mm**. The four unchanged M5 bolt centers around each station are at ±13 mm X and ±13 mm Y.
- Optional 60 mm drill jig has matching four M5 mount holes and a Ø3 mm CENTER PILOT. With receiver hardware removed, register the jig to those holes and lightly spot a 3 mm pilot. REMOVE jig and enlarge center hole to Ø9.0 mm through both existing plastic parts separately. Protect interior components, inspect both sides, deburr, and test stud travel BEFORE reassembling.
- The purchased M8 stud can now advance through the top of the receiver and the newly drilled floor/backing stack for more adjustability. Check PC, wiring and other inside clearances when the threaded shaft is raised fully.
- The rear receivers and their 45 mm + 55 mm extension stacks are **unchanged** from V1.19. Removing the 55 mm front extensions changes the slope; measure real cabinet angle with installed feet and adjust rear height if needed.
- A roughly **2.1 mm nominal minimum plastic web** separates the central nut pocket corners from the existing large M5 socket channels. PETG layer adhesion, nut friction, stud torque, bolt reach and physical load/strength are NOT VERIFIED. Print and test one front receiver with real hardware first. Do not over-tighten or use the pilot jig as a load-bearing washer.

## Validation and source
CAD assembly checks: **71 printable model pieces** (down from 81) and 20 previous small fit samples, plus 2 new standalone M8 test/jig pieces, all validated independently. No detected CAD solid interference. Original shared assemblies, both original floor panels, all four top backing plates and two rear leg stacks are preserved. Source: `viewer/cad/portable-pinball-v1_20/` in the project repository. V1.19 remains separately available. The STL files are printable placeholders pending a real nut/foot fit and cabinet load check.
