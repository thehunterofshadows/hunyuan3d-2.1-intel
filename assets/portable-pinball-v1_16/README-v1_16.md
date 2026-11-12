# Portable Pinball V1.16 — M6×30 tool-free screw-on feet

V1.15 and all previous versions remain separately selectable and unchanged. **Each modular leg section consists of three separate PETG prints (core, stepped bolt key and locking sleeve)** plus a standard M6×30 metal hex-head bolt and a metal M6 hex nut. After a one-time hand assembly, the stacked sections are adjusted by twisting them together without tools. The individual sections are **45 mm tall**; the exposed male bolt thread is nominally **9.5 mm** above each section. Existing mounting stations, M4 through-bolts and 4 mm floor plates stay in place. All dimensions in mm.

## Hardware required for modeled 4-foot setup

- **6 M6 × 30 mm hex-head bolts**: one per 45-mm screw-on section (front 1 × 2 corners; rear 2 × 2 corners). These should be full-thread or have threads for their last 9.5 mm.
- **10 metal M6 hex nuts**: one captive nut in each of 4 fixed receivers and 6 twist sections.
- **4 M6 male-stem rubber swivel feet**, purchased separately (the black pads in Studio are visual references only).
- **16 M4 bolts and nuts plus suitable washers**, unchanged from V1.15, to secure four receiver plates to their inside backing plates through the floor.
- **NO M6×50 bolts** are needed for this V1.16 configuration.

The captive bolt-head pocket assumes **standard M6 external hex-head bolts**, about 10 mm across flats with a head at most 6 mm tall. M6 socket-head/cap/button-head bolts have different head shapes and will NOT lock against rotation in this pocket. If your existing M6×30 bolts are Allen/socket-head or otherwise different, the locking pocket must be revised before printing. Do not rely on glue or a round bolt head jammed in a hex hole.

## How the screw-on section works

Each 45 mm section has coaxial male and female M6 fasteners, not the alternating off-axis bolts from V1.15. The core has a lower side-entry 6 mm-high M6 hex-nut pocket (10.95 mm entry width; nominal 12.1 mm polygon circumcircle) and a higher side entry for a 6 mm-high hex-bolt-head pocket. The bolt shank runs up through the core and protrudes 9.5 mm. The nut and bolt head are **separated by about 9.5 mm of plastic** in the middle section. The printed stepped key fills the bolt's radial loading path, maintaining its centering and preventing the bolt head from escaping/rotating. A hexagonal sleeve slides down from the top, covering and trapping the key and bolt; two small PETG tabs snap into matching sleeve relief pockets. The hex sleeve and core rotate together when hand-tightened. The metal M6 nut below receives the next section's male bolt or the commercial swivel foot's threaded stem.

**One-time print assembly:**
1. Print one receiver (`foot_receiver_left_rear.stl`) and the complete first modular section (`foot_twist_core_left_rear_1_45mm.stl`, `foot_bolt_key_left_rear_1_45mm.stl`, `foot_lock_sleeve_left_rear_1_45mm.stl`). Use the enclosed print-first kit ZIP for these files.
2. With the core upright, slide a real standard M6 nut into the lower side-opening. A shallow PETG nub is designed to retain it before mating; never force it if too tight.
3. Insert an M6×30 **hex-head** bolt laterally into the upper head cavity with its thread pointing upward. Then slide the stepped printed key in from the same side, filling both head and shaft channels.
4. Slide the keyed hexagonal sleeve down **over the entire printed core** from the exposed-bolt end until its bottom meets the wide 11 mm base rim and the retention nibs engage. Check that the bolt **cannot rotate independently, tilt, or fall out**, and that the key cannot escape. Actual PETG snap behavior is NOT established by CAD checks alone.
5. Prepare the receivers by sliding M6 nuts into their centered side-loading slots; first install each receiver to the 4-mm floor using four original M4 through-bolts into its internal 50-mm backing plate, using a tool small enough to fit the existing 10-mm access bores.
6. Twist a section's protruding male M6 bolt into the centered captive M6 nut of the receiver or section directly above. Hand-tighten the whole printed cylinder, not the loose bolt. Use one modular section at each front corner and two at each rear corner to match the shown viewer configuration.
7. Twist the purchased M6 swivel rubber foot stem into the bottom nut of the lowest section. Confirm the metal stem has **at least several fully engaged threads without approaching the upper bolt-head pocket**. Do not assume any rubber pad's stem is exactly the visual reference length.

The system also permits using **zero sections at front** (M6 rubber foot stem straight into the fixed receiver) and **one section at rear**, keeping the whole cabinet lower while maintaining the same 45-mm rear/front step. Never raise one side by itself. If you want different lift increments, we can later introduce a shorter **terminal-only female spacer**, but it would no longer contain a 30-mm captive male bolt.

## Important fit / strength limits

- This revision assumes hex-head M6 bolts. Standard hex heads vary slightly by manufacturer; print the small kit before doing all feet. Pocket openings are nominal, not verified with your physical hardware.
- Test the stepped key, sleeve snap retention, torque transmission, M6 nut insertion, and repeated hand assembly/disassembly. No claim of actual tool-free reliability is made until a real PETG print is tested.
- The original 4-mm floor-to-wall joints have NOT been mechanically load certified. Side nudges and button pressure can impose bending and rocking loads. Test on a scrap floor coupon and secure/reinforce the floor-to-wall load path before mounting the finished cabinet.
- CAD solid and interference checks passed for **71 printable parts**; all **91 exported STLs (71 parts + 20 fit coupons)** passed closed manifold, single-shell and print-bed-placement checks. This is NOT a load or strength test.
- Retain V1.15 as fallback if the screw-on sleeve and nut/bolt fit prove inconvenient.
