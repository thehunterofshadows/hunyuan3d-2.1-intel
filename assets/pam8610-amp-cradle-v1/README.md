# PAM8610 mini amp glue-on cradle V1

Independent 3D-printable mounting accessory for Chico pinball.
Source board is the photographed PAM8610 V0.0.4 mini stereo amplifier.

## Dimensions — IMPORTANT ACCURACY NOTE
* Published board size: **31 x 25 x 2.5 mm** (module, NOT the IC).
* **27.48 x 22.93 mm outside-to-outside hole spans were measured by user with calipers.**
* Assuming PCB mounting holes Ø3.00 mm: pitch **24.48 x 19.93 mm center-to-center**.
  Formula center pitch = outside-edge span - one hole diameter.
* Ø3.00 mm is a DESIGN ASSUMPTION, not yet measured; exact pitch remains unverified.
* Measure the real PCB mounting-hole diameter to calculate the final center pitch.
  If not 3.00 mm, change HOLE_D and regenerate before using this cradle.
  Test the gauge against all four real holes BEFORE installing any inserts or gluing.
* Base outer size: 39 x 33 x 11.1 mm overall (including standoffs); flat bottom.
* Four Ø7.4 mm standoffs at +/−12.24 mm X, +/−9.965 mm Y (provisional).
* PCB nominal underside = z11.1 mm, giving 8.3 mm gap above the base.
* Four **M3 heat-set inserts**, user's nominal 5 mm OD by 6 mm length.
* **4.3 mm Ø insert pilots** (versus 4.5 mm on Chico volume box), 6.65 mm deep,
  installed FROM TOP; tiny 4.7 mm mouth relief. Blind, bottom remains unbroken.
* Cradle open on all sides for speaker, power and input wires.
* Suggested PCB mounting screws: M3x8, verify screw/board/insert clearance and don't
  force a screw against the blind pocket bottom.

## Print & mount
1. Measure PCB mounting-hole diameter, then print `pcb_hole_pitch_gauge.stl`
   (1.5 mm thick) and test against all four PCB holes. If even one misses, DO NOT force the screws or glue the cradle.
2. Print `m3_insert_fit_coupon.stl`: 4.2, 4.3 and 4.4 mm test pockets.
   Use 4.3mm production cradle only if the real inserts fit with secure plastic.
3. Print `amp_cradle.stl` flat on its bottom in PETG, 0.2 mm layers, 4 walls,
   30% infill recommended, no supports required.
4. Seat heat inserts from the TOP with a controlled soldering iron, square, away
   from electronics. Allow to cool completely. Never drive screws to bottom.
5. Screw PCB to posts, keeping all pads and exposed contacts clear of screw heads.
   Use gentle torque; check board flex and clear solder joints.
6. Test powered operation and thermal behavior BEFORE gluing down. Disconnect.
7. Roughen and clean the smooth underside of the cradle and cabinet bonding area.
   Use an adhesive suitable for PETG and the chosen cabinet surface (e.g., appropriate
   2-part epoxy); clamp and allow full cure. Hot glue alone may soften near heat.
   Keep the amp ventilated and wires strain-relieved.
8. Keep glue away from the board, standoffs and insert mouths.

The viewer shows a dark **nominal PCB envelope for fit illustration only**;
no physical board, PCB trace, or mounting CAD drawing was supplied.
All fit measurements are provisional until physical gauge test.
