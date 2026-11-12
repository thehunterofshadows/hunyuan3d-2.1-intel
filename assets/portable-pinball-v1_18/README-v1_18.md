# Portable Pinball V1.18 — corrected M6 screw-in access and push-in M6/M8 nut keepers

V1.18 is a **new, separately selectable model**. V1.17 and all earlier releases remain intact. The cabinet, controls, monitor, floor and four M4 receiver-to-floor mounting positions stay unchanged. V1.18 makes **two mechanical improvements** to the tool-free modular feet and a third fit adjustment based on an actual printed-part report.

## 1. Correct missing M6 female bolt-entry hole

The original V1.17 45 mm M6-to-M6 upper rear spacer had a captive M6 nut, but its bottom face was solid beneath the nut. This prevented a subsequent spacer's 9.5 mm exposed M6 male bolt from engaging it. Each of the two upper rear twist cores now has a **6.7 mm nominal centered clearance bore, 11.3 mm deep from the lower face** (the M6 nut remains in its existing 6 mm-high hexagonal side pocket at Z=3–9 mm relative to that face). This leaves the separate M6 bolt-head pocket above, beginning 18.5 mm above the base, undisturbed. The four fixed mounting receivers already have M6 access bores and the lowest 55 mm terminals already have M8 blind foot-stem bores; those retain their respective sizes.

## 2. Push-in captive-nut retaining clips

Each side-inserted metal hex nut is now secured during preassembly by a **removable printed PETG push-in plug**. These retainers use two compliant side catches with recessed snap pockets and a small fingernail relief for removal. A plug does **not** replace the metal nut or take the cabinet's structural load.

- **Six M6 nut clips**: four for the fixed underfloor receivers and two for the 45 mm upper rear spacers.
- **Four M8 nut clips**: one in each 55 mm terminal piece that receives your purchased M8 swivel rubber foot.
- Print one of each type first. The clips are intentionally separate printable pieces, and their corresponding receivers/cores have new snap-recess geometry. Do not assume the V1.18 clips will lock into old V1.17 prints.
- Put the real metal M6/M8 nut into the side-entry slot first, then slide the corresponding plug into that same slot until the catches engage. The bolt or foot stud then threads into the **metal nut**.

## 3. Tighter existing bolt-head retention key

Based on an actual print-fit observation that the captured M6 bolt wiggles unless its original stepped key is pressed further inward, **the key's head-facing surface moves inward by 0.55 mm** (offset reduced from 6.65 to 6.10 mm from the bolt center axis). The shaft-facing portion remains unchanged. The adjustment is applied to all six existing M6 bolt-retaining keys (45 and 55 mm sections). The intended nominal clearance to a standard M6 **10 mm across-flats external hex head** is about 0.33 mm at its circumradius; real bolt-head style, size, print shrinkage and snap retention must still be tested. If your physical bolt is an Allen/socket head, these keys cannot be assumed to work.

## Hardware and installation

- **6 × M6×30 external-hex-head machine bolts**, one in each printed 45/55 mm screw-on section.
- **6 × standard M6 metal hex nuts**, four in the underfloor receivers plus two in the rear 45 mm upper spacers.
- **4 × standard M8 metal hex nuts**, one in each lowest 55 mm terminal.
- **4 × purchased M8 rubber swivel feet**. Each terminal retains a nominal **21 mm deep blind** 8.7 mm M8 stud clearance hole; real stem insertion must be checked and controlled so it does not bottom out.
- **16 M4 mounting bolts and nuts**, with washers, remain the unchanged receiver floor fasteners. These original mounting fasteners require a driver during installation, but twisting the already prepared leg sections remains tool-free.

The modeled configuration has one 55 mm terminal per front corner; each rear corner has one 45 mm M6↔M6 spacer above one 55 mm M6↔M8 terminal. Rear feet therefore have 45 mm extra spacer height. Do not raise only one side.

## Print only one rear corner first

The included `m6-m8-nut-retainer-fit-kit-v1_18.zip` contains exactly the relevant rear-left receiver, rear-left upper spacer, rear-left M8 terminal, and all 3 matching nut-retaining clips, plus the original printed bolt keys and sleeves. Print it, use your physical M6/M8 nuts and existing M6 bolts, and check:

1. Can each M6/M8 nut slide fully into its matching hex pocket without forcing or spin?
2. Does each plug snap in without cracking, retain the nut while handling, and release with reasonable effort?
3. Does the new 11.3 mm lower M6 entry bore allow the exposed M6 thread to reach the captive M6 nut without hitting solid PETG?
4. Is the **new 0.55 mm tighter** bolt-head key better at preventing wobble without needing force or binding?
5. Does the purchased M8 foot stem fit and have adequate thread engagement without exceeding the terminal's **21 mm blind-bore depth**?
6. Do the M4-mounted 4 mm floor panels and the floor-to-wall connection carry the real cabinet's weight and lateral nudge/button forces without rocking or flexing? This structural requirement remains **unverified**.

CAD/STEP, GLB and **81 printable parts plus 20 independent fit STLs** were generated. Automated solid/keepout checks and all **101 manifold STL geometry checks** passed. They do not establish PETG mechanical strength, snap endurance, bolt clamp force, metal-part fit or load rating. V1.17 is preserved for rollback.
