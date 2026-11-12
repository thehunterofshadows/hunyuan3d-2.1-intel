# Portable Pinball V1.17 — M6 twist connectors, M8 rubber swivel feet

**V1.17 keeps all cabinet and floor mounting positions from V1.16 and preserves V1.16 as a selectable older version.** The only intentional design change is to the bottommost twist-on section of each adjustable foot. Normal connectors remain M6×30 bolts into metal M6 hex nuts. The terminal (lowest) module still has a captured M6×30 hex-head bolt protruding upward but has a **side-loaded, captive standard M8 hex nut** on its lower face. Your bought **M8-threaded swivel rubber pad** screws straight into that last M8 nut. No M8 studs need to be built into the 45 mm upper sections.

## Printed geometry

- **Upper optional spacer** (rear pair only): Original 45 mm M6↔M6 twist section, 3 PETG prints (core, keeper, sleeve). M6×30 hex-head bolt at top, M6 nut at bottom.
- **Terminal** (each of 4 corners): 55 mm tall M6↔M8 twist section, 3 PETG prints (core, anti-rotation key, locking sleeve). M6×30 hex-head bolt at top, M8 hex nut below. The terminal is 10 mm longer than the old 45 mm section to keep a **21 mm blind bore** available for the M8 male swivel-pad stem without hitting the retained M6 bolt head.
- **Fixed receiver** (4 positions): Original M6 female center nut receiver with four M4 through-bolts and an inside load-spreading plate. The existing M4 floor fastener pattern is unmodified.
- Both front feet: receiver + 55 mm M6/M8 terminal + M8 swivel pad.
- Both rear feet: receiver + 45 mm M6 spacer + 55 mm M6/M8 terminal + M8 swivel pad. This leaves rear stacks 45 mm longer than fronts.

## Metal hardware (four complete feet, as shown)

- **6 × M6×30 external-hex-head bolts**, all captured in the printed 45/55 mm sections. Standard socket-head bolts need a different hex-head pocket, so check your actual bolts.
- **6 × standard M6 hex nuts**, captive in four receivers and two upper 45 mm rear spacers.
- **4 × standard M8 hex nuts**, captive in the four 55 mm terminal sections.
- **4 × purchased M8 threaded swivel rubber feet**. Their M8 studs must not project more than the **21 mm blind stud-hole depth** from the face of each terminal; shorten/exclude extra insertion with an M8 jam nut or appropriate spacing only after confirming adequate thread engagement and stability. DO NOT force a longer stud into the printed stop.
- The original **16 M4 mounting bolts and nuts**, with washers, remain as in V1.16.

**Nominal M8 nut pocket:** hexagonal circumdiameter 15.5 mm (13.42 mm across flats), depth 8.0 mm, nut flats aligned for side insertion through the 14.0 mm throat, opening 3 mm above the bottom face; 8.7 mm M8 stud clearance and 21 mm maximum insertion. A little printed entry tooth helps retain the loose nut before the swivel foot is screwed in. Actual M8 nut dimensions and PETG printing tolerance vary. Never force a stuck nut into PETG.

## Assembly, completely tool-free height changes

1. Print a *single rear foot test kit* first: 8 STL files (`foot_receiver_left_rear`, `foot_backing_left_rear`, 3 original rear M6 spacer pieces and 3 new 55 mm M8 terminal pieces). Each piece is independently downloadable from Studio as well.
2. Slide a standard **M6 nut** into the fixed receiver; install receiver and backing plate using the original M4 bolts (these initial mounting fasteners may require a screwdriver).
3. Load each **M6×30 external hex-head bolt** sideways into its 45 or 55 mm twist core, thread pointing toward the upper mating receiver. Insert the matching stepped anti-rotation printed key, then snap on its printed hex torque sleeve to trap the bolt head and stop it rotating.
4. On the 45 mm upper rear section, insert an **M6 nut** into its female lower end. On the 55 mm lower terminal, insert an **M8 nut** into the larger female slot. They are purposely different and **not interchangeable**.
5. Hand-twist the prepared parts into the metal M6 nuts in the receivers/upper spacers. Finally thread the purchased **M8 foot stem into the lower M8 nut**, staying within the nominal 21 mm maximum bore depth. Once these captive fasteners are loaded, height adjustments use **no tools**.

## Verification and cautions

The source CAD builder passed solid validity, 71 printable-part geometry, saved cabinet keepouts, and no-printable-part-intersection tests. The full 91-piece STL set (71 printable components + 20 fit samples) passed manifold and printer envelope checks. The M8 hex pocket was checked as an actual CAD void and the M8 stud bore is *blind*, with retained plastic between it and the M6 bolt-head pocket. Actual bolt heads, M8 hex nuts, M8 swivel pad stud lengths, PETG snap/torque retention, screw preload, and mechanical load stability **have not been tested physically**.

The whole design loads through 4 mm removable floor panels; verify floor-to-wall load-bearing and button/nudge side loads on a bench before installing a powered cabinet. V1.16 is preserved as a fallback.
